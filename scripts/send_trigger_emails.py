#!/usr/bin/env python3
"""
Send automated trigger emails: Near Limit, Idle Users.
Run daily via cron: python scripts/send_trigger_emails.py
Or: docker compose exec api python scripts/send_trigger_emails.py
"""
import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.db import async_session_maker
from api.email import send_idle_user_email, send_near_limit_email
from api.models import Deployment, Job, User
from api.usage_service import get_current_period_usage, get_limits_for_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IDLE_DAYS = 3
NEAR_LIMIT_MIN = 0.70
NEAR_LIMIT_MAX = 1.0


async def send_near_limit_emails(db: AsyncSession) -> int:
    """Find free users at 70-100% of limit, send email if not sent this month."""
    result = await db.execute(select(User).where(User.plan.in_(["free", "starter"])))
    users = result.scalars().all()
    now = datetime.now(timezone.utc)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sent = 0
    for user in users:
        if user.near_limit_email_sent_at and user.near_limit_email_sent_at >= current_month_start:
            continue
        token_limit, cpu_limit, gpu_limit = await get_limits_for_user(db, user.id)
        tokens_used, cpu_used, gpu_used = await get_current_period_usage(db, user.id)

        ratios = []
        if token_limit > 0:
            ratios.append(tokens_used / token_limit)
        if cpu_limit > 0:
            ratios.append(cpu_used / cpu_limit)
        if gpu_limit > 0 and gpu_used > 0:
            ratios.append(gpu_used / gpu_limit)

        if not ratios:
            continue
        max_ratio = max(ratios)
        if NEAR_LIMIT_MIN <= max_ratio <= NEAR_LIMIT_MAX:
            try:
                await send_near_limit_email(user.email)
                user.near_limit_email_sent_at = datetime.now(timezone.utc)
                sent += 1
            except Exception as e:
                logger.warning("Near limit email failed for %s: %s", user.email, e)
    return sent


async def send_idle_user_emails(db: AsyncSession) -> int:
    """Find users inactive 3+ days, send reactivation email if not sent in last 7 days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=IDLE_DAYS)
    idle_cutoff = datetime.now(timezone.utc) - timedelta(days=7)  # Don't resend within 7 days

    result = await db.execute(select(User))
    users = result.scalars().all()
    sent = 0

    for user in users:
        if not user.email:
            continue
        if user.idle_email_sent_at and user.idle_email_sent_at > idle_cutoff:
            continue

        job_result = await db.execute(select(func.max(Job.created_at)).where(Job.user_id == user.id))
        last_job = job_result.scalar()
        dep_result = await db.execute(
            select(func.max(Deployment.created_at)).where(Deployment.user_id == user.id)
        )
        last_dep = dep_result.scalar()
        last_activity = max((x for x in (last_job, last_dep) if x is not None), default=None)
        if last_activity is None:
            continue
        if last_activity > cutoff:
            continue

        try:
            await send_idle_user_email(user.email)
            user.idle_email_sent_at = datetime.now(timezone.utc)
            sent += 1
        except Exception as e:
            logger.warning("Idle user email failed for %s: %s", user.email, e)
    return sent


async def main() -> None:
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured. Skipping trigger emails.")
        sys.exit(0)

    async with async_session_maker() as db:
        try:
            near = await send_near_limit_emails(db)
            idle = await send_idle_user_emails(db)
            await db.commit()
            logger.info("Trigger emails: near_limit=%d, idle=%d", near, idle)
        except Exception as e:
            logger.exception("Trigger emails failed: %s", e)
            await db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
