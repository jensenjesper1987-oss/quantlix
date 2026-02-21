"""Application configuration."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "cloud"
    postgres_password: str = "cloud_secret"
    postgres_db: str = "cloud"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "models"
    jwt_secret: str = "dev-secret-change-me"

    # Email (Sweego). Set to False to disable all email until domain is verified.
    # Use SWEEGO_API_KEY for HTTP API (recommended in K8s; avoids SMTP port blocking).
    # Otherwise use SMTP with smtp_user/smtp_password.
    email_enabled: bool = True
    sweego_api_key: str = ""  # When set, use Sweego HTTP API instead of SMTP
    sweego_auth_type: str = "api_key"  # "api_key" (Api-Key, Sweego default), "api_token" (Api-Token), or "bearer" (Authorization: Bearer)
    smtp_host: str = "smtp.sweego.io"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "support@quantlix.ai"
    smtp_from_name: str = "Quantlix"
    app_base_url: str = "https://api.quantlix.ai"  # For verification links
    portal_base_url: str = "https://www.quantlix.ai"  # For Stripe redirects
    dev_return_verification_link: bool = False  # If True, include verification link in signup response (for local testing)

    # Usage limits (0 = unlimited)
    usage_limit_tokens_per_month: int = 0
    usage_limit_compute_seconds_per_month: float = 0.0

    # CORS (comma-separated extra origins, e.g. for Vercel: https://quantlix.vercel.app)
    cors_origins: str = ""

    # Logging (DEBUG, INFO, WARNING, ERROR)
    log_level: str = "INFO"

    # Guardrails
    guardrail_timeout_seconds: float = 5.0
    guardrail_fail_open: bool = True  # Allow on error; False = block on error
    guardrail_block_max_per_window: int = 5
    guardrail_block_window_seconds: int = 300

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_starter: str = ""  # Price ID for Starter €9/mo
    stripe_price_id_pro: str = ""  # Price ID for Pro plan (e.g. price_xxx)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()
