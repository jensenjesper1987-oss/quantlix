"""Email sending via Heysender SMTP."""
import logging

import aiosmtplib
from email.message import EmailMessage

from api.config import settings

logger = logging.getLogger(__name__)


def _is_email_configured() -> bool:
    return bool(settings.smtp_user and settings.smtp_password)


async def send_verification_email(to_email: str, token: str) -> bool:
    """Send email verification link. Returns True if sent, False if skipped (no SMTP config)."""
    if not _is_email_configured():
        logger.warning("SMTP not configured; skipping verification email to %s", to_email)
        return False

    verify_url = f"{settings.app_base_url.rstrip('/')}/auth/verify?token={token}"
    subject = "Verify your Quantlix account"
    body = f"""Hello,

Please verify your email address by clicking the link below:

{verify_url}

This link expires in 24 hours. If you didn't create an account, you can ignore this email.

— Quantlix
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send verification email to %s: %s", to_email, e)
        raise


async def send_password_reset_email(to_email: str, token: str) -> bool:
    """Send password reset link. Returns True if sent, False if skipped (no SMTP config)."""
    if not _is_email_configured():
        logger.warning("SMTP not configured; skipping password reset email to %s", to_email)
        return False

    reset_url = f"{settings.app_base_url.rstrip('/')}/auth/reset-password?token={token}"
    subject = "Reset your Quantlix password"
    body = f"""Hello,

You requested a password reset. Click the link below to set a new password:

{reset_url}

This link expires in 1 hour. If you didn't request this, you can ignore this email.

— Quantlix
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Password reset email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send password reset email to %s: %s", to_email, e)
        raise


async def send_first_deploy_email(to_email: str) -> bool:
    """Send 'Your endpoint is live' email after first deploy. Builds trust."""
    if not _is_email_configured():
        logger.warning("SMTP not configured; skipping first deploy email to %s", to_email)
        return False

    subject = "Your Quantlix endpoint is live"
    body = """Nice work.

If anything felt confusing, tell me — I'm fixing issues daily. Just reply to this email.

— Quantlix
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("First deploy email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send first deploy email to %s: %s", to_email, e)
        raise


async def send_near_limit_email(to_email: str) -> bool:
    """Send near-limit warning. Upgrade to keep models running."""
    if not _is_email_configured():
        logger.warning("SMTP not configured; skipping near limit email to %s", to_email)
        return False

    subject = "You're close to your monthly limit"
    pricing_url = f"{settings.portal_base_url.rstrip('/')}/pricing"
    body = f"""Upgrade to keep your models running smoothly.

{pricing_url}

— Quantlix
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Near limit email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send near limit email to %s: %s", to_email, e)
        raise


async def send_idle_user_email(to_email: str) -> bool:
    """Send reactivation email after 3 days inactive."""
    if not _is_email_configured():
        logger.warning("SMTP not configured; skipping idle user email to %s", to_email)
        return False

    subject = "Still working on your model?"
    body = """If something blocked you, tell me — I can help. Just reply to this email.

— Quantlix
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Idle user email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send idle user email to %s: %s", to_email, e)
        raise
