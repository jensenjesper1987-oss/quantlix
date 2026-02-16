"""
Quantlix — REST API
POST /auth/signup, POST /auth/login, POST /deploy, POST /run, GET /status, GET /usage
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy import text
from api.config import settings
from api.db import Base, engine
from api.models import APIKey, Deployment, Job, UsageRecord, User
from api.routes import auth, billing, deploy, health, jobs, run, status, usage

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://app.quantlix.ai",
    "https://quantlix.ai",
]


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
    yield
    await engine.dispose()


app = FastAPI(
    title="Quantlix API",
    version="0.1.0",
    lifespan=lifespan,
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
app.include_router(run.router, prefix="/run", tags=["run"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(usage.router, prefix="/usage", tags=["usage"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])


@app.get("/")
async def root():
    return {"service": "quantlix", "version": "0.1.0"}
