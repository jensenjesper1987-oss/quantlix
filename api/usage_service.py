"""Usage tracking and limit enforcement."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import User, UsageRecord
from api.models import UserPlan, PLAN_LIMITS


def _period_start_end() -> tuple[datetime, datetime]:
    """Current calendar month (UTC)."""
    today = date.today()
    start = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
    if today.month == 12:
        end = datetime(today.year, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
    else:
        end = datetime(today.year, today.month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    return start, end


async def get_current_period_usage(
    db: AsyncSession,
    user_id: str,
) -> tuple[int, float, float]:
    """Return (tokens_used, cpu_seconds, gpu_seconds) for the current period (month)."""
    start, end = _period_start_end()
    result = await db.execute(
        select(
            func.coalesce(func.sum(UsageRecord.tokens_used), 0).label("tokens"),
            func.coalesce(func.sum(UsageRecord.compute_seconds), 0).label("cpu"),
            func.coalesce(func.sum(UsageRecord.gpu_seconds), 0).label("gpu"),
        ).where(
            UsageRecord.user_id == user_id,
            UsageRecord.created_at >= start,
            UsageRecord.created_at <= end,
        )
    )
    row = result.one()
    return int(row.tokens), float(row.cpu), float(row.gpu)


def get_limits_for_plan(plan: str) -> tuple[int, float, float]:
    """Return (token_limit, cpu_limit, gpu_limit) for a plan."""
    try:
        return PLAN_LIMITS[UserPlan(plan)]
    except (ValueError, KeyError):
        return PLAN_LIMITS[UserPlan.FREE]


async def get_limits_for_user(db: AsyncSession, user_id: str) -> tuple[int, float, float]:
    """Return (token_limit, cpu_limit, gpu_limit) for a user based on their plan."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    plan = (user.plan or UserPlan.FREE.value) if user else UserPlan.FREE.value
    return get_limits_for_plan(plan)


async def check_usage_limits(
    db: AsyncSession,
    user_id: str,
    *,
    is_gpu_job: bool = False,
) -> tuple[bool, str | None]:
    """
    Check if user is within their plan limits. Returns (ok, error_message).
    For GPU jobs, checks gpu_limit. For CPU jobs, checks cpu_limit.
    """
    token_limit, cpu_limit, gpu_limit = await get_limits_for_user(db, user_id)
    tokens_used, cpu_used, gpu_used = await get_current_period_usage(db, user_id)

    if token_limit > 0 and tokens_used >= token_limit:
        return False, f"Token limit reached ({tokens_used:,}/{token_limit:,} this month). Upgrade to Pro for more."
    if is_gpu_job:
        if gpu_limit <= 0:
            return False, "GPU deployment requires Pro plan. Upgrade to unlock 2h GPU/month."
        # Pro: allow overage (tracked for billing at €0.50/hr)
    else:
        if cpu_limit > 0 and cpu_used >= cpu_limit:
            return False, f"Compute limit reached ({cpu_used:.0f}s/{cpu_limit:.0f}s this month). Upgrade to Pro for more."

    return True, None
