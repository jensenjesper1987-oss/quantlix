"""Run inference endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
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
    job = Job(
        user_id=user.id,
        deployment_id=deployment.id,
        input_data=input_payload,
        status=JobStatus.QUEUED.value,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    await enqueue_job(
        job_id=job.id,
        payload={
            "deployment_id": deployment.id,
            "user_id": user.id,
            "input": input_payload,
        },
    )

    return RunResponse(
        job_id=job.id,
        status=job.status,
        message="Inference job queued",
    )
