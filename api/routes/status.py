"""Status endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Deployment, Job
from api.schemas import StatusResponse

router = APIRouter()


@router.get("/{resource_id}", response_model=StatusResponse)
async def get_status(
    resource_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get status of deployment or job."""
    # Try deployment first
    result = await db.execute(
        select(Deployment).where(
            Deployment.id == resource_id,
            Deployment.user_id == user.id,
        )
    )
    deployment = result.scalar_one_or_none()
    if deployment:
        return StatusResponse(
            id=deployment.id,
            type="deployment",
            status=deployment.status,
            created_at=deployment.created_at,
            updated_at=deployment.updated_at,
            error_message=deployment.error_message,
        )

    # Try job
    result = await db.execute(
        select(Job).where(
            Job.id == resource_id,
            Job.user_id == user.id,
        )
    )
    job = result.scalar_one_or_none()
    if job:
        return StatusResponse(
            id=job.id,
            type="job",
            status=job.status,
            created_at=job.created_at,
            updated_at=job.completed_at,
            error_message=job.error_message,
            output_data=job.output_data,
            tokens_used=job.tokens_used,
            compute_seconds=job.compute_seconds,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found",
    )
