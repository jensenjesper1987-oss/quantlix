"""Pydantic schemas for API request/response."""
import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# --- Auth helpers ---
PASSWORD_MIN_LENGTH = 12
PASSWORD_SPECIAL_CHARS = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]")


def _check_password_strength(password: str) -> tuple[bool, int, list[str]]:
    """Check password strength. Returns (valid, score, feedback)."""
    feedback: list[str] = []
    score = 0
    if len(password) >= PASSWORD_MIN_LENGTH:
        score += 1
    else:
        feedback.append(f"At least {PASSWORD_MIN_LENGTH} characters")
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("At least one uppercase letter")
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("At least one lowercase letter")
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("At least one digit")
    if PASSWORD_SPECIAL_CHARS.search(password):
        score += 1
    else:
        feedback.append("At least one special character (!@#$%^&* etc.)")
    return (len(feedback) == 0, score, feedback)


def _validate_password_strength(password: str) -> str:
    """Validate password meets strength requirements. Raises ValueError with specific message."""
    valid, _, feedback = _check_password_strength(password)
    if not valid:
        raise ValueError(feedback[0] if feedback else "Password does not meet requirements")
    return password


# --- Deploy ---
class DeployRequest(BaseModel):
    model_id: str = Field(..., description="Model identifier (e.g. my-llama-7b)")
    model_path: str | None = Field(None, description="MinIO path to model files (e.g. models/user123/llama)")
    config: dict = Field(default_factory=dict, description="Deployment config: replicas, resources, etc.")


class DeployResponse(BaseModel):
    deployment_id: str
    status: str
    message: str = "Deployment queued"


# --- Run ---
class RunRequest(BaseModel):
    deployment_id: str = Field(..., description="ID of deployed model")
    input: Any = Field(..., description="Inference input (JSON)")


class RunResponse(BaseModel):
    job_id: str
    status: str
    message: str = "Inference job queued"


# --- Jobs (list) ---
class JobListItem(BaseModel):
    id: str
    deployment_id: str
    status: str
    tokens_used: int | None = None
    compute_seconds: float | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class JobListResponse(BaseModel):
    jobs: list[JobListItem]


# --- Status ---
class StatusResponse(BaseModel):
    id: str
    type: str = Field(..., description="deployment or job")
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    error_message: str | None = None
    # Job-specific
    output_data: dict | None = None
    tokens_used: int | None = None
    compute_seconds: float | None = None


# --- Auth ---
def _validate_email_not_disposable(email: str) -> str:
    """Reject disposable/temp-mail domains."""
    from api.disposable_domains import is_disposable_email

    if is_disposable_email(email):
        raise ValueError("Disposable email addresses are not allowed")
    return email


class SignupRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description=f"Password (min {PASSWORD_MIN_LENGTH} chars, uppercase, lowercase, digit, special char)",
    )

    @field_validator("email")
    @classmethod
    def validate_email_not_disposable(cls, v: str) -> str:
        return _validate_email_not_disposable(v)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    api_key: str = Field(..., description="API key for X-API-Key header")
    user_id: str = Field(..., description="User ID")


class SignupResponse(BaseModel):
    message: str = Field(..., description="Status message")
    email: str = Field(..., description="Email address verification was sent to")
    verification_link: str | None = Field(None, description="Verification URL (only in dev mode when email may not arrive)")


class ResendVerificationRequest(BaseModel):
    email: str = Field(..., description="Email to resend verification to")


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Email to send reset link to")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Reset token from email link")
    new_password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description=f"New password (min {PASSWORD_MIN_LENGTH} chars, uppercase, lowercase, digit, special char)",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class PasswordStrengthRequest(BaseModel):
    password: str = Field(..., description="Password to check")


class PasswordStrengthResponse(BaseModel):
    valid: bool = Field(..., description="Whether password meets all requirements")
    score: int = Field(..., ge=0, le=5, description="Strength score 0-5")
    feedback: list[str] = Field(default_factory=list, description="List of requirements not met")


class APIKeyInfo(BaseModel):
    id: str = Field(..., description="API key ID")
    name: str | None = Field(None, description="Key name/label")
    created_at: datetime = Field(..., description="When the key was created")


class APIKeyListResponse(BaseModel):
    api_keys: list[APIKeyInfo] = Field(..., description="List of API keys")


class CreateAPIKeyRequest(BaseModel):
    name: str | None = Field(None, max_length=100, description="Optional name for the key")


class CreateAPIKeyResponse(BaseModel):
    api_key: str = Field(..., description="New API key (shown only once)")
    id: str = Field(..., description="Key ID")
    name: str | None = Field(None, description="Key name")


class RotateAPIKeyResponse(BaseModel):
    api_key: str = Field(..., description="New API key (old key revoked)")
    id: str = Field(..., description="Key ID")
    name: str | None = Field(None, description="Key name")


class UpgradeRequest(BaseModel):
    plan: str = Field(..., description="Plan to upgrade to (e.g. 'pro')")


class UserMeResponse(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    plan: str = Field(..., description="Current plan (free, pro)")


# --- Usage ---
class UsageDailyPoint(BaseModel):
    date: date
    tokens_used: int = 0
    compute_seconds: float = 0.0
    gpu_seconds: float = 0.0
    job_count: int = 0


class UsageHistoryResponse(BaseModel):
    daily: list[UsageDailyPoint]


class MetricsResponse(BaseModel):
    success_rate: float = Field(..., description="Fraction of completed jobs (0-1)")
    total_jobs: int = 0
    avg_latency_s: float | None = Field(None, description="Avg inference latency in seconds")
    p50_latency_s: float | None = Field(None, description="Median latency in seconds")
    p95_latency_s: float | None = Field(None, description="P95 latency in seconds")


class UsageResponse(BaseModel):
    user_id: str
    plan: str = Field(..., description="Current plan (free, pro)")
    tokens_used: int = 0
    compute_seconds: float = 0.0
    gpu_seconds: float = 0.0
    job_count: int = 0
    start_date: date | None = None
    end_date: date | None = None
    # Limits (0 = unlimited)
    tokens_limit: int | None = Field(None, description="Monthly token limit (0 = unlimited)")
    compute_limit: float | None = Field(None, description="Monthly CPU compute limit in seconds (0 = unlimited)")
    gpu_limit: float | None = Field(None, description="Monthly GPU limit in seconds (0 = none, Pro only)")
    gpu_seconds_overage: float | None = Field(None, description="GPU seconds over limit (billed at €0.50/hr)")
