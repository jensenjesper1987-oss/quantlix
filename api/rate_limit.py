"""Redis-based rate limiting for auth endpoints."""
from __future__ import annotations

from fastapi import Request
from redis.asyncio import Redis

from api.queue import get_redis
from api.schemas import ResendVerificationRequest

RATE_LIMIT_SIGNUP = 5
RATE_LIMIT_SIGNUP_WINDOW = 3600  # 1 hour
RATE_LIMIT_LOGIN = 10
RATE_LIMIT_LOGIN_WINDOW = 900  # 15 minutes
RATE_LIMIT_VERIFY = 20
RATE_LIMIT_VERIFY_WINDOW = 900  # 15 minutes
RATE_LIMIT_RESEND = 3
RATE_LIMIT_RESEND_WINDOW = 3600  # 1 hour
RATE_LIMIT_PASSWORD_CHECK = 30
RATE_LIMIT_PASSWORD_CHECK_WINDOW = 900  # 15 minutes
RATE_LIMIT_FORGOT_PASSWORD = 3
RATE_LIMIT_FORGOT_PASSWORD_WINDOW = 3600  # 1 hour
RATE_LIMIT_RESET_PASSWORD = 10
RATE_LIMIT_RESET_PASSWORD_WINDOW = 900  # 15 minutes


def _client_ip(request: Request) -> str:
    """Get client IP, respecting X-Forwarded-For and X-Real-IP."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "unknown"


async def _check_rate_limit(
    redis: Redis,
    key: str,
    limit: int,
    window: int,
) -> None:
    """Increment counter and raise 429 if over limit."""
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window)
    if count > limit:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
        )


async def rate_limit_signup(request: Request) -> None:
    """Rate limit signup: 5 attempts per hour per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:signup:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_SIGNUP,
            window=RATE_LIMIT_SIGNUP_WINDOW,
        )
    finally:
        await redis.aclose()


async def rate_limit_login(request: Request) -> None:
    """Rate limit login: 10 attempts per 15 minutes per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:login:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_LOGIN,
            window=RATE_LIMIT_LOGIN_WINDOW,
        )
    finally:
        await redis.aclose()


async def rate_limit_verify(request: Request) -> None:
    """Rate limit verify: 20 attempts per 15 minutes per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:verify:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_VERIFY,
            window=RATE_LIMIT_VERIFY_WINDOW,
        )
    finally:
        await redis.aclose()


def _email_key_safe(email: str) -> str:
    """Make email safe for Redis key (no colons etc)."""
    return email.strip().lower().replace("@", "_at_")


async def rate_limit_resend(request: Request, body: ResendVerificationRequest) -> None:
    """Rate limit resend: 3 attempts per hour per IP and per email."""
    ip = _client_ip(request)
    email_safe = _email_key_safe(body.email)
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            f"rate_limit:auth:resend:ip:{ip}",
            limit=RATE_LIMIT_RESEND,
            window=RATE_LIMIT_RESEND_WINDOW,
        )
        await _check_rate_limit(
            redis,
            f"rate_limit:auth:resend:email:{email_safe}",
            limit=RATE_LIMIT_RESEND,
            window=RATE_LIMIT_RESEND_WINDOW,
        )
    finally:
        await redis.aclose()


async def rate_limit_password_check(request: Request) -> None:
    """Rate limit password strength check: 30 per 15 min per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:password_check:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_PASSWORD_CHECK,
            window=RATE_LIMIT_PASSWORD_CHECK_WINDOW,
        )
    finally:
        await redis.aclose()


async def rate_limit_forgot_password(request: Request) -> None:
    """Rate limit forgot password: 3 per hour per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:forgot_password:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_FORGOT_PASSWORD,
            window=RATE_LIMIT_FORGOT_PASSWORD_WINDOW,
        )
    finally:
        await redis.aclose()


async def rate_limit_reset_password(request: Request) -> None:
    """Rate limit reset password: 10 per 15 min per IP."""
    ip = _client_ip(request)
    key = f"rate_limit:auth:reset_password:{ip}"
    redis = await get_redis()
    try:
        await _check_rate_limit(
            redis,
            key,
            limit=RATE_LIMIT_RESET_PASSWORD,
            window=RATE_LIMIT_RESET_PASSWORD_WINDOW,
        )
    finally:
        await redis.aclose()
