"""
Quantlix — REST API
POST /auth/signup, POST /auth/login, POST /deploy, POST /run, GET /status, GET /usage
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.logging_config import setup_logging

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)
from prometheus_client import make_asgi_app
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import Base, engine, async_session_maker
from api.metrics import (
    quantlix_usage_compute_seconds_total,
    quantlix_usage_gpu_seconds_total,
    quantlix_usage_jobs_total,
    quantlix_usage_tokens_total,
    quantlix_users_by_plan,
    quantlix_users_total,
    quantlix_users_verified,
)
from api.models import UsageRecord, User
from api.routes import auth, billing, deploy, deployments, health, jobs, run, status, usage

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://www.quantlix.ai",
    "https://quantlix.ai",
]


async def _refresh_metrics(session: AsyncSession) -> None:
    """Query DB and update Prometheus gauges for users, usage, tiers."""
    # Users total and by plan
    total = await session.scalar(select(func.count(User.id)))
    quantlix_users_total.set(total or 0)

    verified = await session.scalar(select(func.count(User.id)).where(User.email_verified == True))
    quantlix_users_verified.set(verified or 0)

    by_plan = await session.execute(
        select(User.plan, func.count(User.id)).where(User.plan.is_not(None)).group_by(User.plan)
    )
    for plan, count in by_plan:
        quantlix_users_by_plan.labels(plan=plan or "free").set(count)

    # Usage this month
    start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage = await session.execute(
        select(
            func.coalesce(func.sum(UsageRecord.tokens_used), 0),
            func.coalesce(func.sum(UsageRecord.compute_seconds), 0),
            func.coalesce(func.sum(UsageRecord.gpu_seconds), 0),
            func.count(UsageRecord.id),
        ).where(UsageRecord.created_at >= start_of_month)
    )
    row = usage.one()
    quantlix_usage_tokens_total.set(int(row[0]))
    quantlix_usage_compute_seconds_total.set(float(row[1]))
    quantlix_usage_gpu_seconds_total.set(float(row[2]))
    quantlix_usage_jobs_total.set(int(row[3]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add password_hash if missing (migration for existing DBs)
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMPTZ"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS plan VARCHAR(20) DEFAULT 'free'"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)"))
        await conn.execute(text("ALTER TABLE usage_records ADD COLUMN IF NOT EXISTS gpu_seconds DOUBLE PRECISION DEFAULT 0"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_deploy_email_sent BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS near_limit_email_sent_at TIMESTAMPTZ"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS idle_email_sent_at TIMESTAMPTZ"))
        await conn.run_sync(Base.metadata.create_all)  # Create deployment_revisions if missing

    async def update_metrics():
        """Periodically update Prometheus metrics for users, usage, tiers."""
        while True:
            try:
                async with async_session_maker() as session:
                    await _refresh_metrics(session)
            except Exception as e:
                logger.exception("Metrics refresh failed: %s", e)
            await asyncio.sleep(60)

    # Initial refresh + background task
    async with async_session_maker() as session:
        await _refresh_metrics(session)
    task = asyncio.create_task(update_metrics())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await engine.dispose()


app = FastAPI(
    title="Quantlix API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Log HTTP exceptions (especially 5xx) and return JSON response."""
    if exc.status_code >= 500:
        logger.error(
            "HTTP %d: %s %s - %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail) if exc.detail else "Internal server error"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unhandled exceptions and return 500."""
    logger.exception(
        "Unhandled exception: %s %s - %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def _get_cors_origins() -> list[str]:
    origins = list(DEFAULT_CORS_ORIGINS)
    if settings.cors_origins:
        origins.extend(o.strip() for o in settings.cors_origins.split(",") if o.strip())
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Routes
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(deploy.router, prefix="/deploy", tags=["deploy"])
app.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
app.include_router(run.router, prefix="/run", tags=["run"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(usage.router, prefix="/usage", tags=["usage"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])


@app.get("/")
async def root():
    return {"service": "quantlix", "version": "0.1.0"}
