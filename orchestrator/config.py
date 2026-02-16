"""Orchestrator configuration."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "cloud"
    postgres_password: str = "cloud_secret"
    postgres_db: str = "cloud"
    redis_url: str = "redis://localhost:6379/0"
    kubeconfig: str = ""  # Empty = in-cluster; set path for local dev
    mock_k8s: bool = False  # True = simulate completion without real K8s (for dev)
    inference_url: str = ""  # When mock_k8s: call this for real inference (e.g. http://inference:8080)
    inference_image: str = "quantlix-inference:latest"  # K8s Job container image

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
