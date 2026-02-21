"""Deployments list, revisions, and rollback."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Deployment, DeploymentRevision
from api.schemas import (
    DeploymentListItem,
    DeploymentListResponse,
    DeploymentRevisionItem,
    DeploymentRevisionListResponse,
    RollbackResponse,
)

router = APIRouter()


@router.get("", response_model=DeploymentListResponse)
async def list_deployments(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List user's deployments with revision counts. Supports pagination."""
    # Total count
    count_result = await db.scalar(
        select(func.count(func.distinct(Deployment.id))).where(
            Deployment.user_id == user.id
        )
    )
    total = count_result or 0

    result = await db.execute(
        select(
            Deployment.id,
            Deployment.model_id,
            Deployment.status,
            Deployment.created_at,
            Deployment.updated_at,
            func.count(DeploymentRevision.id).label("revision_count"),
        )
        .outerjoin(DeploymentRevision, Deployment.id == DeploymentRevision.deployment_id)
        .where(Deployment.user_id == user.id)
        .group_by(Deployment.id)
        .order_by(Deployment.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
    return DeploymentListResponse(
        deployments=[
            DeploymentListItem(
                id=r.id,
                model_id=r.model_id,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
                revision_count=r.revision_count or 0,
            )
            for r in rows
        ],
        total=total,
    )


@router.get("/{deployment_id}/revisions", response_model=DeploymentRevisionListResponse)
async def list_revisions(
    deployment_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List revisions for a deployment (newest first)."""
    result = await db.execute(
        select(Deployment).where(
            Deployment.id == deployment_id,
            Deployment.user_id == user.id,
        )
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    revs = await db.execute(
        select(DeploymentRevision)
        .where(DeploymentRevision.deployment_id == deployment_id)
        .order_by(DeploymentRevision.revision_number.desc())
    )
    revisions = revs.scalars().all()
    return DeploymentRevisionListResponse(
        deployment_id=deployment_id,
        revisions=[
            DeploymentRevisionItem(
                revision_number=r.revision_number,
                model_id=r.model_id,
                model_path=r.model_path,
                config=r.config or {},
                created_at=r.created_at,
            )
            for r in revisions
        ],
    )


@router.post("/{deployment_id}/rollback", response_model=RollbackResponse)
async def rollback(
    deployment_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    revision: int = Query(..., ge=1, description="Revision number to rollback to"),
):
    """Rollback deployment to a previous revision."""
    result = await db.execute(
        select(Deployment).where(
            Deployment.id == deployment_id,
            Deployment.user_id == user.id,
        )
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    rev_result = await db.execute(
        select(DeploymentRevision).where(
            DeploymentRevision.deployment_id == deployment_id,
            DeploymentRevision.revision_number == revision,
        )
    )
    rev = rev_result.scalar_one_or_none()
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revision {revision} not found")

    deployment.model_id = rev.model_id
    deployment.model_path = rev.model_path
    deployment.config = rev.config
    return RollbackResponse(deployment_id=deployment_id, revision=revision)
