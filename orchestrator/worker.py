"""
Redis queue worker — Consumes jobs, schedules on K8s, updates DB.
Scaling: HPA on queue depth (custom metric).
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from prometheus_client import Gauge
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.db import async_session_maker
from api.email import send_first_deploy_email
from api.guardrails.base import GuardrailAction, GuardrailResult
from api.guardrails.block_rate import increment_block_count
from api.guardrails.config import get_guardrail_config
from api.guardrails.runner import run_guardrails
from api.models import Deployment, DeploymentStatus, Job, JobStatus, UsageRecord, User
from api.policies.policy import PolicyConfig, PolicyAction, apply_policy
from api.scoring.scorer import compute_score
from orchestrator.config import settings
from orchestrator.inference_client import call_inference_http, read_inference_result_from_redis
from orchestrator.k8s import create_inference_job, wait_for_job_completion

logger = logging.getLogger(__name__)

INFERENCE_QUEUE = "inference:queue"


def _serialize_flags(results: list[GuardrailResult]) -> dict | None:
    """Serialize FLAG results to JSON-serializable dict for storage."""
    flags = [{"rule": r.rule_name, "message": r.message, "details": r.details} for r in results if r.action == GuardrailAction.FLAG]
    return {"flags": flags} if flags else None
queue_depth = Gauge("inference_queue_depth", "Number of jobs in inference queue")


async def update_queue_metric(redis: Redis) -> None:
    """Update Prometheus gauge with current queue length."""
    try:
        depth = await redis.llen(INFERENCE_QUEUE)
        queue_depth.set(depth)
    except Exception:
        pass


async def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def process_job(payload: dict) -> None:
    """Process a single inference job: update status, run K8s, record usage."""
    job_id = payload.get("job_id")
    deployment_id = payload.get("deployment_id")
    user_id = payload.get("user_id")
    input_data = payload.get("input", {})

    if not all([job_id, deployment_id, user_id]):
        logger.error("Invalid job payload: missing job_id, deployment_id, or user_id")
        return

    async with async_session_maker() as db:
        try:
            # Fetch job and deployment (job_id only — payload is trusted from our queue)
            result = await db.execute(
                select(Job, Deployment).join(
                    Deployment, Job.deployment_id == Deployment.id
                ).where(Job.id == job_id)
            )
            row = result.one_or_none()
            if not row:
                logger.error(
                    "Job %s not found (job does not exist in DB)",
                    job_id,
                )
                return

            job, deployment = row
            user_id = str(job.user_id)  # Use job's user_id for block_rate, usage, etc.

            # Update job to RUNNING
            job.status = JobStatus.RUNNING.value
            await db.flush()

            # Ensure deployment is READY (lazy deploy)
            if deployment.status == DeploymentStatus.PENDING.value:
                deployment.status = DeploymentStatus.DEPLOYING.value
                await db.flush()
                # For MVP: no real model deploy, just mark ready
                deployment.status = DeploymentStatus.READY.value
                # Send first-deploy email if user hasn't received it yet
                result_user = await db.execute(select(User).where(User.id == user_id))
                user_row = result_user.scalar_one_or_none()
                if user_row and not user_row.first_deploy_email_sent:
                    try:
                        await send_first_deploy_email(user_row.email)
                        user_row.first_deploy_email_sent = True
                    except Exception as e:
                        logger.warning("Failed to send first deploy email: %s", e)

            await db.commit()

            # Run inference (K8s, inference HTTP, or mock)
            is_gpu = bool(deployment.config and deployment.config.get("gpu"))
            job_name = await create_inference_job(
                job_id=job_id,
                deployment_id=deployment_id,
                user_id=user_id,
                model_id=deployment.model_id,
                input_data=input_data,
                use_gpu=is_gpu,
            )

            inference_result: dict | None = None
            if job_name:
                success, err = await wait_for_job_completion(job_name)
                if success:
                    inference_result = await read_inference_result_from_redis(job_id)
            elif settings.inference_url:
                # Mock K8s but real inference via HTTP
                inference_result = await call_inference_http(job_id, input_data)
                success = inference_result is not None
                err = None if success else "Inference service unavailable"
            else:
                # Pure mock: simulate completion
                await asyncio.sleep(1)
                success, err = True, None

            # Update job and create UsageRecord
            async with async_session_maker() as db2:
                result = await db2.execute(
                    select(Job, Deployment).join(
                        Deployment, Job.deployment_id == Deployment.id
                    ).where(Job.id == job_id)
                )
                row = result.one()
                job, deployment = row

                if success:
                    output_data = inference_result.get("output_data", {"result": "ok"}) if inference_result else {"result": "ok", "mock": True}
                    job.output_data = output_data
                    job.tokens_used = inference_result.get("tokens_used", 100) if inference_result else 100
                    job.compute_seconds = inference_result.get("compute_seconds", 1.5) if inference_result else 1.5
                    job.completed_at = datetime.now(timezone.utc)

                    # Guardrails & scoring
                    cfg = deployment.config or {}
                    policy_cfg = PolicyConfig(
                        block_threshold=cfg.get("policy", {}).get("block_threshold", 0.3),
                        log_threshold=cfg.get("policy", {}).get("log_threshold", 0.7),
                    )
                    logger.info(
                        "Guardrails: deployment=%s config=%s policy_cfg=%s",
                        deployment.id, cfg, (policy_cfg.block_threshold, policy_cfg.log_threshold),
                    )
                    enabled_rules, rule_config, fail_open, gr_timeout = get_guardrail_config(deployment)
                    input_passed, input_results = run_guardrails(
                        input_data, "input", enabled_rules, rule_config,
                        timeout_seconds=gr_timeout, fail_open=fail_open
                    )
                    output_passed, output_results = run_guardrails(
                        output_data, "output", enabled_rules, rule_config,
                        timeout_seconds=gr_timeout, fail_open=fail_open
                    )

                    job.guardrail_blocked = not output_passed
                    job.guardrail_flags = _serialize_flags(input_results + output_results)

                    score_input = compute_score(None, None, input_results, [])
                    score_output = compute_score(None, None, [], output_results)
                    score_final = compute_score(None, None, input_results, output_results)
                    job.score_input = score_input
                    job.score_output = score_output
                    job.score_final = score_final

                    if not output_passed:
                        job.status = JobStatus.FAILED.value
                        job.policy_action = "block"
                        job.error_message = next((r.message for r in output_results if r.action == GuardrailAction.BLOCK), "Output blocked by guardrails")
                        # Increment block count for rate limiting (cost control)
                        window = cfg.get("guardrail_block_window", settings.guardrail_block_window_seconds)
                        await increment_block_count(str(user_id), str(deployment.id), window)
                    else:
                        policy_action, reason = apply_policy(score_final, policy_cfg)
                        logger.info(
                            "Policy: score_final=%.2f action=%s reason=%s",
                            score_final, policy_action.value, reason,
                        )
                        job.policy_action = policy_action.value
                        if policy_action == PolicyAction.BLOCK:
                            job.status = JobStatus.FAILED.value
                            job.error_message = reason
                            job.output_data = None
                            window = cfg.get("guardrail_block_window", settings.guardrail_block_window_seconds)
                            await increment_block_count(str(user_id), str(deployment.id), window)
                        else:
                            job.status = JobStatus.COMPLETED.value
                            if policy_action == PolicyAction.LOG:
                                logger.warning("Job %s logged for review: %s", job_id, reason)

                    secs = job.compute_seconds or 0.0
                    is_gpu = bool(deployment.config and deployment.config.get("gpu"))
                    if job.status == JobStatus.COMPLETED.value:
                        usage = UsageRecord(
                            user_id=user_id,
                            job_id=job_id,
                            tokens_used=job.tokens_used or 0,
                            compute_seconds=0.0 if is_gpu else secs,
                            gpu_seconds=secs if is_gpu else 0.0,
                        )
                        db2.add(usage)
                else:
                    job.status = JobStatus.FAILED.value
                    job.error_message = err
                    job.completed_at = datetime.now(timezone.utc)

                await db2.commit()
                logger.info("Job %s completed: %s", job_id, job.status)

        except Exception as e:
            logger.exception("Job %s failed: %s", job_id, e)
            async with async_session_maker() as db2:
                result = await db2.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    job.status = JobStatus.FAILED.value
                    job.error_message = str(e)
                    job.completed_at = datetime.now(timezone.utc)
                    await db2.commit()


async def run_worker() -> None:
    """Consume jobs from Redis queue indefinitely."""
    redis = await get_redis()
    logger.info("Worker started, consuming from %s", INFERENCE_QUEUE)

    while True:
        try:
            await update_queue_metric(redis)
            # Blocking pop with 5s timeout (allows graceful shutdown)
            result = await redis.blpop(INFERENCE_QUEUE, timeout=5)
            if not result:
                continue

            _, raw = result
            payload = json.loads(raw)
            await process_job(payload)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("Worker error: %s", e)
            await asyncio.sleep(5)

    await redis.aclose()
