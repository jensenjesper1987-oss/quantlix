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

from api.db import async_session_maker
from api.email import send_first_deploy_email
from api.models import Deployment, DeploymentStatus, Job, JobStatus, UsageRecord, User
from orchestrator.config import settings
from orchestrator.inference_client import call_inference_http, read_inference_result_from_redis
from orchestrator.k8s import create_inference_job, wait_for_job_completion

logger = logging.getLogger(__name__)

INFERENCE_QUEUE = "inference:queue"
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
            # Fetch job and deployment
            result = await db.execute(
                select(Job, Deployment).join(
                    Deployment, Job.deployment_id == Deployment.id
                ).where(
                    Job.id == job_id,
                    Job.user_id == user_id,
                )
            )
            row = result.one_or_none()
            if not row:
                logger.error("Job %s not found", job_id)
                return

            job, deployment = row

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
                    job.status = JobStatus.COMPLETED.value
                    if inference_result:
                        job.output_data = inference_result.get("output_data", {"result": "ok"})
                        job.tokens_used = inference_result.get("tokens_used", 100)
                        job.compute_seconds = inference_result.get("compute_seconds", 1.5)
                    else:
                        job.output_data = {"result": "ok", "mock": True}
                        job.tokens_used = 100
                        job.compute_seconds = 1.5
                    job.completed_at = datetime.now(timezone.utc)

                    secs = job.compute_seconds or 0.0
                    is_gpu = bool(deployment.config and deployment.config.get("gpu"))
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
