"""Run inference endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.config import settings
from api.db import get_db
from api.guardrails.base import GuardrailAction
from api.guardrails.block_rate import check_block_rate_limit
from api.guardrails.config import get_guardrail_config
from api.guardrails.runner import run_guardrails
from api.models import Deployment, DeploymentStatus, Job, JobStatus
from api.queue import enqueue_job
from api.schemas import RunRequest, RunResponse
from api.usage_service import check_usage_limits

router = APIRouter()




@router.post("", response_model=RunResponse)
async def run_inference(
    body: RunRequest,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
):
    """Run inference on a deployed model."""
    result = await db.execute(
        select(Deployment).where(
            Deployment.id == body.deployment_id,
            Deployment.user_id == user.id,
        )
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )

    is_gpu = bool(deployment.config and deployment.config.get("gpu"))
    ok, err = await check_usage_limits(db, user.id, is_gpu_job=is_gpu)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=err,
        )

    if deployment.status not in (DeploymentStatus.READY.value, DeploymentStatus.PENDING.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deployment not runnable (status: {deployment.status})",
        )

    input_payload = body.input if isinstance(body.input, dict) else {"data": body.input}

    # Block rate limit — prevent repeated blocked outputs from multiplying cost
    cfg = deployment.config or {}
    max_blocks = cfg.get("guardrail_block_max", settings.guardrail_block_max_per_window)
    window_secs = cfg.get("guardrail_block_window", settings.guardrail_block_window_seconds)
    rate_result = await check_block_rate_limit(
        str(user.id), str(deployment.id), max_blocks, window_secs
    )
    if not rate_result.within_limit:
        response.headers["Retry-After"] = str(rate_result.retry_after_seconds)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"Too many blocked requests. Retry after {rate_result.retry_after_seconds}s",
                "blocks_in_window": rate_result.blocks_in_window,
                "max_blocks": rate_result.max_blocks,
                "retry_after_seconds": rate_result.retry_after_seconds,
            },
        )

    # Input guardrails — block before enqueue if any rule blocks
    enabled_rules, rule_config, fail_open, timeout = get_guardrail_config(deployment)
    passed, guardrail_results = run_guardrails(
        input_payload, "input", enabled_rules, rule_config,
        timeout_seconds=timeout, fail_open=fail_open
    )
    if not passed:
        blocked = next((r for r in guardrail_results if r.action == GuardrailAction.BLOCK), None)
        retry_secs = 60
        response.headers["Retry-After"] = str(retry_secs)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": blocked.message if blocked else "Request blocked by guardrails",
                "retry_after_seconds": retry_secs,
            },
        )
    job = Job(
        user_id=user.id,
        deployment_id=deployment.id,
        input_data=input_payload,
        status=JobStatus.QUEUED.value,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    await db.commit()  # Commit before enqueue so orchestrator can find the job

    await enqueue_job(
        job_id=job.id,
        payload={
            "deployment_id": deployment.id,
            "user_id": user.id,
            "input": input_payload,
        },
    )

    block_rate = None
    if rate_result.blocks_in_window > 0:
        block_rate = {
            "blocks_in_window": rate_result.blocks_in_window,
            "max_blocks": rate_result.max_blocks,
        }
    return RunResponse(
        job_id=job.id,
        status=job.status,
        message="Inference job queued",
        block_rate=block_rate,
    )
