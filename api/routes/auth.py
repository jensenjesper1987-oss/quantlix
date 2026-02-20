"""Auth endpoints: signup, login, email verification, password reset."""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import CurrentAPIKey, CurrentUser, hash_api_key, hash_password, verify_password
from api.db import get_db
from api.email import send_password_reset_email, send_verification_email
from api.models import APIKey, User, UserPlan
from api.rate_limit import (
    rate_limit_forgot_password,
    rate_limit_login,
    rate_limit_password_check,
    rate_limit_resend,
    rate_limit_reset_password,
    rate_limit_signup,
    rate_limit_verify,
)
from api.config import settings
from api.schemas import (
    APIKeyInfo,
    APIKeyListResponse,
    AuthResponse,
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    ForgotPasswordRequest,
    LoginRequest,
    PasswordStrengthRequest,
    PasswordStrengthResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    RotateAPIKeyResponse,
    SignupRequest,
    SignupResponse,
    UpgradeRequest,
    UserMeResponse,
)
from api.schemas import _check_password_strength

PASSWORD_RESET_EXPIRY_HOURS = 1

router = APIRouter()


def _generate_api_key() -> str:
    """Generate a secure API key."""
    return f"qxl_{secrets.token_hex(24)}"


def _generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


@router.post("/check-password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(
    body: PasswordStrengthRequest,
    _: None = Depends(rate_limit_password_check),
):
    """Check password strength (for UI strength meter). Returns valid, score 0-5, and feedback."""
    valid, score, feedback = _check_password_strength(body.password)
    return PasswordStrengthResponse(valid=valid, score=score, feedback=feedback)


@router.post("/signup", response_model=SignupResponse)
async def signup(
    body: SignupRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(rate_limit_signup),
):
    """Create a new user and send verification email."""
    try:
        return await _do_signup(body, db)
    except HTTPException:
        raise
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception("Signup failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


async def _do_signup(body: SignupRequest, db: AsyncSession) -> SignupResponse:
    """Create a new user and send verification email (if email enabled)."""
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    token = _generate_verification_token()
    email_enabled = settings.email_enabled
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        email_verified=not email_enabled,  # Auto-verify when email disabled
        email_verification_token=token if email_enabled else None,
    )
    db.add(user)
    await db.commit()

    if email_enabled:
        try:
            sent = await send_verification_email(body.email, token)
            if sent:
                message = "Verification email sent. Check your inbox and click the link to activate your account."
            else:
                message = (
                    "Account created. Email not configured (set SWEEGO_API_KEY or SMTP credentials). "
                    "Contact support@quantlix.ai to verify your account."
                )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Signup: verification email failed for %s: %s", body.email, e
            )
            message = (
                "Account created. We couldn't send the verification email (check email config). "
                "Contact support@quantlix.ai to verify your account."
            )
    else:
        message = "Account created. You can log in immediately (email verification disabled)."
        plain_key = _generate_api_key()
        api_key = APIKey(
            user_id=user.id,
            key_hash=hash_api_key(plain_key),
            name="signup",
        )
        db.add(api_key)
        await db.commit()
        return SignupResponse(
            message=message,
            email=body.email,
            verification_link=None,
            api_key=plain_key,
            user_id=user.id,
        )

    verification_link = None
    if email_enabled and settings.dev_return_verification_link:
        verification_link = f"{settings.portal_base_url.rstrip('/')}/verify?token={token}"
    return SignupResponse(
        message=message,
        email=body.email,
        verification_link=verification_link,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(rate_limit_login),
):
    """Verify credentials and return an API key."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if settings.email_enabled and not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox for the verification link.",
        )
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    plain_key = _generate_api_key()
    api_key = APIKey(
        user_id=user.id,
        key_hash=hash_api_key(plain_key),
        name="login",
    )
    db.add(api_key)
    await db.commit()

    return AuthResponse(api_key=plain_key, user_id=user.id)


@router.get("/verify", response_model=AuthResponse)
async def verify_email(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Query(..., description="Verification token from email"),
    _: None = Depends(rate_limit_verify),
):
    """Verify email address and return API key."""
    result = await db.execute(
        select(User).where(User.email_verification_token == token)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link.",
        )
    user.email_verified = True
    user.email_verification_token = None

    plain_key = _generate_api_key()
    api_key = APIKey(
        user_id=user.id,
        key_hash=hash_api_key(plain_key),
        name="default",
    )
    db.add(api_key)
    await db.commit()

    return AuthResponse(api_key=plain_key, user_id=user.id)


@router.post("/resend-verification")
async def resend_verification(
    body: ResendVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(rate_limit_resend),
):
    """Resend verification email."""
    if not settings.email_enabled:
        return {"message": "Email verification is disabled. You can log in directly."}
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user:
        # Don't reveal whether email exists
        return {"message": "If that email is registered, a verification link was sent."}
    if user.email_verified:
        return {"message": "Email is already verified. You can log in."}
    token = _generate_verification_token()
    user.email_verification_token = token
    await db.commit()

    try:
        await send_verification_email(body.email, token)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Resend verification email failed for %s: %s", body.email, e)
        # Still return success; don't reveal whether email exists or send failed

    out: dict = {"message": "Verification email sent. Check your inbox."}
    if settings.dev_return_verification_link:
        out["verification_link"] = f"{settings.portal_base_url.rstrip('/')}/verify?token={token}"
    return out


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(rate_limit_forgot_password),
):
    """Request password reset. Sends email with reset link if account exists."""
    if not settings.email_enabled:
        return {"message": "Password reset is not available. Contact support@quantlix.ai."}
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        return {"message": "If that email is registered, a reset link was sent."}
    token = _generate_verification_token()
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)
    await db.commit()

    await send_password_reset_email(body.email, token)

    return {"message": "If that email is registered, a reset link was sent."}


def _escape_js(s: str) -> str:
    """Escape string for safe use in JavaScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(
    token: str = Query(..., description="Reset token from email"),
):
    """Serve a simple form to reset password (for users who click the email link)."""
    from api.config import settings

    base = settings.app_base_url.rstrip("/")
    token_escaped = _escape_js(token)
    return f"""<!DOCTYPE html>
<html>
<head><title>Reset Password - Quantlix</title></head>
<body style="font-family:sans-serif;max-width:400px;margin:50px auto;padding:20px">
  <h1>Reset your password</h1>
  <p>Enter your new password below (min 12 chars, upper, lower, digit, special).</p>
  <form id="resetForm">
    <p><label>New password: <input type="password" id="pw" required minlength="12"></label></p>
    <p><button type="submit">Reset password</button></p>
  </form>
  <p id="msg" style="margin-top:1em"></p>
  <p style="color:#666;font-size:0.9em">Or use the CLI: quantlix reset-password &lt;token&gt; -p &lt;new-password&gt;</p>
  <script>
    document.getElementById("resetForm").onsubmit = async (e) => {{
      e.preventDefault();
      const pw = document.getElementById("pw").value;
      const msg = document.getElementById("msg");
      try {{
        const r = await fetch("{base}/auth/reset-password", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ token: "{token_escaped}", new_password: pw }})
        }});
        const d = await r.json().catch(() => ({{}}));
        if (r.ok) {{
          msg.innerHTML = '<span style="color:green">' + (d.message || "Password reset! You can now log in.") + '</span>';
        }} else {{
          msg.innerHTML = '<span style="color:red">' + (d.detail || "Reset failed") + '</span>';
        }}
      }} catch (err) {{
        msg.innerHTML = '<span style="color:red">' + err.message + '</span>';
      }}
    }};
  </script>
</body>
</html>"""


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(rate_limit_reset_password),
):
    """Reset password using token from email link."""
    result = await db.execute(
        select(User).where(User.password_reset_token == body.token)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link.",
        )
    if not user.password_reset_expires_at or user.password_reset_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset link has expired. Request a new one.",
        )
    user.password_hash = hash_password(body.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    await db.commit()

    return {"message": "Password reset successfully. You can now log in."}


# --- User & plan (requires authentication) ---


@router.get("/me", response_model=UserMeResponse)
async def get_me(user: CurrentUser):
    """Return current user info including plan."""
    return UserMeResponse(
        id=user.id,
        email=user.email,
        plan=user.plan or UserPlan.FREE.value,
    )


@router.post("/upgrade")
async def upgrade_plan(
    body: UpgradeRequest,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Upgrade user plan. In production, this would be driven by Stripe webhooks."""
    try:
        plan = UserPlan(body.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Valid options: {[p.value for p in UserPlan]}",
        )
    if plan == UserPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use downgrade endpoint to switch to free plan.",
        )
    user.plan = plan.value
    await db.commit()
    return {"message": f"Upgraded to {plan.value}", "plan": plan.value}


# --- API key management (requires authentication) ---


@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List API keys for the current user."""
    result = await db.execute(select(APIKey).where(APIKey.user_id == user.id))
    keys = result.scalars().all()
    return APIKeyListResponse(
        api_keys=[
            APIKeyInfo(id=k.id, name=k.name, created_at=k.created_at)
            for k in keys
        ]
    )


@router.post("/api-keys", response_model=CreateAPIKeyResponse)
async def create_api_key(
    body: CreateAPIKeyRequest,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new API key. The key is shown only once."""
    plain_key = _generate_api_key()
    api_key = APIKey(
        user_id=user.id,
        key_hash=hash_api_key(plain_key),
        name=body.name or "api-key",
    )
    db.add(api_key)
    await db.commit()
    return CreateAPIKeyResponse(
        api_key=plain_key,
        id=api_key.id,
        name=api_key.name,
    )


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Revoke an API key. The key will stop working immediately."""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found.",
        )
    await db.delete(key)
    await db.commit()
    return {"message": "API key revoked."}


@router.post("/api-keys/rotate", response_model=RotateAPIKeyResponse)
async def rotate_api_key(
    current_key: CurrentAPIKey,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new API key and revoke the current one. Use the new key from the response."""
    user_id = current_key.user_id
    plain_key = _generate_api_key()
    new_key = APIKey(
        user_id=user_id,
        key_hash=hash_api_key(plain_key),
        name=current_key.name or "rotated",
    )
    db.add(new_key)
    await db.delete(current_key)
    await db.commit()
    return RotateAPIKeyResponse(
        api_key=plain_key,
        id=new_key.id,
        name=new_key.name,
    )
