"""Usage and billing endpoints."""
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentUser
from api.db import get_db
from api.models import Job, JobStatus, UsageRecord
from api.schemas import MetricsResponse, UsageDailyPoint, UsageHistoryResponse, UsageResponse
from api.usage_service import get_limits_for_user

router = APIRouter()


@router.get("", response_model=UsageResponse)
async def get_usage(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date | None = Query(None, description="Start of period"),
    end_date: date | None = Query(None, description="End of period"),
):
    """Get usage stats: tokens_used, compute_seconds, job count, and limits."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    result = await db.execute(
        select(
            func.coalesce(func.sum(UsageRecord.tokens_used), 0).label("tokens_used"),
            func.coalesce(func.sum(UsageRecord.compute_seconds), 0).label("compute_seconds"),
            func.coalesce(func.sum(UsageRecord.gpu_seconds), 0).label("gpu_seconds"),
            func.count(UsageRecord.id).label("job_count"),
        ).where(
            UsageRecord.user_id == user.id,
            UsageRecord.created_at >= start_dt,
            UsageRecord.created_at <= end_dt,
        )
    )
    row = result.one()

    token_limit, cpu_limit, gpu_limit = await get_limits_for_user(db, user.id)
    gpu_used = float(row.gpu_seconds)
    gpu_overage = max(0, gpu_used - gpu_limit) if gpu_limit > 0 else 0

    return UsageResponse(
        user_id=user.id,
        plan=user.plan or "free",
        tokens_used=int(row.tokens_used),
        compute_seconds=float(row.compute_seconds),
        gpu_seconds=float(row.gpu_seconds),
        job_count=int(row.job_count),
        start_date=start_date,
        end_date=end_date,
        tokens_limit=token_limit if token_limit > 0 else None,
        compute_limit=cpu_limit if cpu_limit > 0 else None,
        gpu_limit=gpu_limit if gpu_limit > 0 else None,
        gpu_seconds_overage=gpu_overage if gpu_overage > 0 else None,
    )


@router.get("/history", response_model=UsageHistoryResponse)
async def get_usage_history(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=7, le=90),
):
    """Get daily usage breakdown for charts."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    result = await db.execute(
        select(
            cast(UsageRecord.created_at, Date).label("day"),
            func.coalesce(func.sum(UsageRecord.tokens_used), 0).label("tokens_used"),
            func.coalesce(func.sum(UsageRecord.compute_seconds), 0).label("compute_seconds"),
            func.coalesce(func.sum(UsageRecord.gpu_seconds), 0).label("gpu_seconds"),
            func.count(UsageRecord.id).label("job_count"),
        )
        .where(
            UsageRecord.user_id == user.id,
            UsageRecord.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc),
            UsageRecord.created_at <= datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc),
        )
        .group_by(cast(UsageRecord.created_at, Date))
        .order_by(cast(UsageRecord.created_at, Date))
    )
    rows = result.all()

    daily = [
        UsageDailyPoint(
            date=row.day,
            tokens_used=int(row.tokens_used),
            compute_seconds=float(row.compute_seconds),
            gpu_seconds=float(row.gpu_seconds),
            job_count=int(row.job_count),
        )
        for row in rows
    ]
    return UsageHistoryResponse(daily=daily)


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=1, le=90),
):
    """Get performance metrics: success rate, latency stats."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Job.status, Job.compute_seconds, Job.completed_at, Job.created_at)
        .where(Job.user_id == user.id, Job.created_at >= cutoff)
    )
    jobs = result.all()

    total = len(jobs)
    completed = sum(1 for j in jobs if j.status in (JobStatus.COMPLETED.value, "completed"))
    success_rate = completed / total if total > 0 else 0.0

    latencies = [j.compute_seconds for j in jobs if j.compute_seconds is not None and j.compute_seconds > 0]
    if not latencies:
        return MetricsResponse(success_rate=success_rate, total_jobs=total)

    latencies_sorted = sorted(latencies)
    avg = sum(latencies_sorted) / len(latencies_sorted)
    p50 = latencies_sorted[len(latencies_sorted) // 2] if latencies_sorted else None
    p95_idx = int(len(latencies_sorted) * 0.95) - 1
    p95 = latencies_sorted[max(0, p95_idx)] if latencies_sorted else None

    return MetricsResponse(
        success_rate=success_rate,
        total_jobs=total,
        avg_latency_s=round(avg, 2),
        p50_latency_s=round(p50, 2),
        p95_latency_s=round(p95, 2),
    )
