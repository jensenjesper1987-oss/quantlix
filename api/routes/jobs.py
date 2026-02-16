"""Jobs endpoints - list recent inference jobs."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Job
from api.schemas import JobListItem, JobListResponse

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
):
    """List recent inference jobs for the current user."""
    result = await db.execute(
        select(Job)
        .where(Job.user_id == user.id)
        .order_by(desc(Job.created_at))
        .limit(limit)
    )
    jobs = result.scalars().all()
    return JobListResponse(
        jobs=[
            JobListItem(
                id=j.id,
                deployment_id=j.deployment_id,
                status=j.status,
                tokens_used=j.tokens_used,
                compute_seconds=j.compute_seconds,
                created_at=j.created_at,
                completed_at=j.completed_at,
            )
            for j in jobs
        ]
    )
