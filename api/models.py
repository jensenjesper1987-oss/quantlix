"""Database models."""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    READY = "ready"
    FAILED = "failed"
    STOPPED = "stopped"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"


# Plan limits: (tokens_per_month, cpu_seconds_per_month, gpu_seconds_per_month)
# Starter: 500k tokens, 5h CPU, priority queue, no GPU
# Pro: 2h GPU included, extra at €0.50/hr
PLAN_LIMITS: dict[UserPlan, tuple[int, float, float]] = {
    UserPlan.FREE: (100_000, 3_600, 0),       # 100k tokens, 1h CPU, no GPU
    UserPlan.STARTER: (500_000, 18_000, 0),   # 500k tokens, 5h CPU, priority queue, no GPU
    UserPlan.PRO: (1_000_000, 36_000, 7_200),  # 1M tokens, 10h CPU, 2h GPU
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)  # bcrypt hash
    email_verified: Mapped[bool] = mapped_column(default=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), default=UserPlan.FREE.value)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Email triggers (avoid duplicate sends)
    first_deploy_email_sent: Mapped[bool] = mapped_column(default=False)
    near_limit_email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idle_email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user")
    deployments: Mapped[list["Deployment"]] = relationship(back_populates="user")
    jobs: Mapped[list["Job"]] = relationship(back_populates="user")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # hashed, never store plain
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="api_keys")


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    model_path: Mapped[str | None] = mapped_column(String(512), nullable=True)  # MinIO path
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(50), default=DeploymentStatus.PENDING.value)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="deployments")
    jobs: Mapped[list["Job"]] = relationship(back_populates="deployment")
    revisions: Mapped[list["DeploymentRevision"]] = relationship(
        back_populates="deployment", order_by="DeploymentRevision.revision_number"
    )

    __table_args__ = (Index("ix_deployments_user_status", "user_id", "status"),)


class DeploymentRevision(Base):
    """Snapshot of deployment config for versioning and rollback."""
    __tablename__ = "deployment_revisions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    deployment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    model_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deployment: Mapped["Deployment"] = relationship(back_populates="revisions")

    __table_args__ = (Index("ix_deployment_revisions_deployment", "deployment_id"),)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    deployment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("deployments.id"), nullable=False)
    input_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)  # MinIO path or inline ref
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=JobStatus.QUEUED.value)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compute_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="jobs")
    deployment: Mapped["Deployment"] = relationship(back_populates="jobs")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="job")

    __table_args__ = (Index("ix_jobs_user_status", "user_id", "status"),)


class UsageRecord(Base):
    """Aggregated usage for billing: user_id, tokens_used, compute_seconds (CPU), gpu_seconds."""
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    job_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    compute_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    gpu_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="usage_records")
    job: Mapped["Job | None"] = relationship(back_populates="usage_records")

    __table_args__ = (Index("ix_usage_user_created", "user_id", "created_at"),)
