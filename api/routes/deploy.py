"""Deploy model endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Deployment, DeploymentStatus
from api.schemas import DeployRequest, DeployResponse

router = APIRouter()


@router.post("", response_model=DeployResponse)
async def deploy(
    body: DeployRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Deploy a model to the inference platform."""
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
