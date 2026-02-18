"""Email sending via Sweego (HTTP API or SMTP)."""
import logging

import aiosmtplib
import httpx
from email.message import EmailMessage

from api.config import settings

logger = logging.getLogger(__name__)

SWEEGO_API_URL = "https://api.sweego.io/send"


def _is_email_configured() -> bool:
    if not settings.email_enabled:
        return False
    if settings.sweego_api_key:
        return True
    return bool(settings.smtp_user and settings.smtp_password)


async def _send_via_sweego_api(to_email: str, subject: str, body: str) -> None:
    """Send email via Sweego HTTP API (port 443, works from K8s)."""
    payload = {
        "channel": "email",
        "provider": "sweego",
        "recipients": [{"email": to_email}],
        "from": {"name": settings.smtp_from_name, "email": settings.smtp_from_email},
        "subject": subject,
        "message-txt": body,
    }
    if settings.sweego_auth_type == "bearer":
        auth_header = ("Authorization", f"Bearer {settings.sweego_api_key}")
    elif settings.sweego_auth_type == "api_key":
        auth_header = ("Api-Key", settings.sweego_api_key)
    else:
        auth_header = ("Api-Token", settings.sweego_api_key)  # default: api_token
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            SWEEGO_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                auth_header[0]: auth_header[1],
            },
        )
        if resp.status_code >= 400:
            body_preview = resp.text[:500] if resp.text else "(empty)"
            logger.error(
                "Sweego API error: status=%s body=%s",
                resp.status_code,
                body_preview,
            )
        resp.raise_for_status()


async def _send_email(to_email: str, subject: str, body: str) -> None:
    """Send email via Sweego API or SMTP depending on config."""
    if settings.sweego_api_key:
        logger.info("Sending email to %s via Sweego API", to_email)
        await _send_via_sweego_api(to_email, subject, body)
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg.set_content(body)
    logger.info("Sending email to %s via %s:%s", to_email, settings.smtp_host, settings.smtp_port)
    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )


async def send_verification_email(to_email: str, token: str) -> bool:
    """Send email verification link. Returns True if sent, False if skipped (no email config)."""
    if not _is_email_configured():
        logger.warning("Email not configured; skipping verification email to %s", to_email)
        return False

    verify_url = f"{settings.app_base_url.rstrip('/')}/auth/verify?token={token}"
    subject = "Verify your Quantlix account"
    body = f"""Hello,

Please verify your email address by clicking the link below:

{verify_url}

This link expires in 24 hours. If you didn't create an account, you can ignore this email.

— Quantlix
"""

    try:
        await _send_email(to_email, subject, body)
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send verification email to %s: %s", to_email, e)
        raise


async def send_password_reset_email(to_email: str, token: str) -> bool:
    """Send password reset link. Returns True if sent, False if skipped (no email config)."""
    if not _is_email_configured():
        logger.warning("Email not configured; skipping password reset email to %s", to_email)
        return False

    reset_url = f"{settings.app_base_url.rstrip('/')}/auth/reset-password?token={token}"
    subject = "Reset your Quantlix password"
    body = f"""Hello,

You requested a password reset. Click the link below to set a new password:

{reset_url}

This link expires in 1 hour. If you didn't request this, you can ignore this email.

— Quantlix
"""

    try:
        await _send_email(to_email, subject, body)
        logger.info("Password reset email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send password reset email to %s: %s", to_email, e)
        raise


async def send_first_deploy_email(to_email: str) -> bool:
    """Send 'Your endpoint is live' email after first deploy. Builds trust."""
    if not _is_email_configured():
        logger.warning("Email not configured; skipping first deploy email to %s", to_email)
        return False

    subject = "Your Quantlix endpoint is live"
    body = """Nice work.

If anything felt confusing, tell me — I'm fixing issues daily. Just reply to this email.

— Quantlix
"""

    try:
        await _send_email(to_email, subject, body)
        logger.info("First deploy email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send first deploy email to %s: %s", to_email, e)
        raise


async def send_near_limit_email(to_email: str) -> bool:
    """Send near-limit warning. Upgrade to keep models running."""
    if not _is_email_configured():
        logger.warning("Email not configured; skipping near limit email to %s", to_email)
        return False

    subject = "You're close to your monthly limit"
    pricing_url = f"{settings.portal_base_url.rstrip('/')}/pricing"
    body = f"""Upgrade to keep your models running smoothly.

{pricing_url}

— Quantlix
"""

    try:
        await _send_email(to_email, subject, body)
        logger.info("Near limit email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send near limit email to %s: %s", to_email, e)
        raise


async def send_idle_user_email(to_email: str) -> bool:
    """Send reactivation email after 3 days inactive."""
    if not _is_email_configured():
        logger.warning("Email not configured; skipping idle user email to %s", to_email)
        return False

    subject = "Still working on your model?"
    body = """If something blocked you, tell me — I can help. Just reply to this email.

— Quantlix
"""

    try:
        await _send_email(to_email, subject, body)
        logger.info("Idle user email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send idle user email to %s: %s", to_email, e)
        raise
