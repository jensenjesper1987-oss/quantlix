"""Deploy model endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Deployment, DeploymentRevision, DeploymentStatus
from api.schemas import DeployRequest, DeployResponse

router = APIRouter()


@router.post("", response_model=DeployResponse)
async def deploy(
    body: DeployRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Deploy a model to the inference platform. Pass deployment_id to update existing (creates new revision)."""
    if body.deployment_id:
        # Update existing deployment: snapshot current to revision, then update
        result = await db.execute(
            select(Deployment).where(
                Deployment.id == body.deployment_id,
                Deployment.user_id == user.id,
            )
        )
        deployment = result.scalar_one_or_none()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        # Create revision snapshot of current state
        rev_count = await db.scalar(
            select(func.count(DeploymentRevision.id)).where(
                DeploymentRevision.deployment_id == deployment.id
            )
        )
        rev_number = (rev_count or 0) + 1
        revision = DeploymentRevision(
            deployment_id=deployment.id,
            revision_number=rev_number,
            model_id=deployment.model_id,
            model_path=deployment.model_path,
            config=deployment.config or {},
        )
        db.add(revision)

        # Update deployment with new config
        deployment.model_id = body.model_id
        deployment.model_path = body.model_path
        deployment.config = body.config
        deployment.status = DeploymentStatus.PENDING.value
        await db.flush()
        await db.refresh(deployment)
        return DeployResponse(
            deployment_id=deployment.id,
            status=deployment.status,
            message="Deployment updated",
            revision=rev_number,
        )

    # New deployment
    deployment = Deployment(
        user_id=user.id,
        model_id=body.model_id,
        model_path=body.model_path,
        config=body.config,
        status=DeploymentStatus.PENDING.value,
    )
    db.add(deployment)
    await db.flush()
    await db.refresh(deployment)
    return DeployResponse(
        deployment_id=deployment.id,
        status=deployment.status,
        message="Deployment queued",
    )
