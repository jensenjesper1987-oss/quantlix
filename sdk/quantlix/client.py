"""
Quantlix Python SDK — Thin wrapper around Quantlix REST API.
"""
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.quantlix.ai"


@dataclass
class DeployResult:
    deployment_id: str
    status: str
    message: str
    revision: int | None = None


@dataclass
class RunResult:
    job_id: str
    status: str
    message: str


@dataclass
class StatusResult:
    id: str
    type: str
    status: str
    created_at: str | None
    updated_at: str | None
    error_message: str | None
    output_data: dict | None
    tokens_used: int | None
    compute_seconds: float | None


@dataclass
class UsageResult:
    user_id: str
    tokens_used: int
    compute_seconds: float
    gpu_seconds: float = 0.0
    job_count: int = 0
    start_date: date | None = None
    end_date: date | None = None
    tokens_limit: int | None = None  # Monthly limit (0/unset = unlimited)
    compute_limit: float | None = None  # Monthly CPU limit in seconds
    gpu_limit: float | None = None  # Monthly GPU limit in seconds (Pro only)
    gpu_seconds_overage: float | None = None  # Extra GPU (billed at €0.50/hr)


@dataclass
class AuthResult:
    api_key: str
    user_id: str


@dataclass
class SignupResult:
    message: str
    email: str


@dataclass
class APIKeyInfo:
    id: str
    name: str | None
    created_at: str


@dataclass
class CreateAPIKeyResult:
    api_key: str
    id: str
    name: str | None


class QuantlixCloudClient:
    """Client for Quantlix API."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "X-API-Key": self.api_key}

    @staticmethod
    def signup(email: str, password: str, base_url: str = DEFAULT_BASE_URL) -> SignupResult:
        """Create account. Sends verification email; use verify_email() after clicking the link."""
        url = base_url.rstrip("/")
        with httpx.Client() as client:
            r = client.post(
                f"{url}/auth/signup",
                json={"email": email, "password": password},
            )
            r.raise_for_status()
            data = r.json()
            return SignupResult(message=data["message"], email=data["email"])

    @staticmethod
    def verify_email(token: str, base_url: str = DEFAULT_BASE_URL) -> AuthResult:
        """Verify email and get API key. Call with token from verification link."""
        url = base_url.rstrip("/")
        with httpx.Client() as client:
            r = client.get(f"{url}/auth/verify", params={"token": token})
            r.raise_for_status()
            data = r.json()
            return AuthResult(api_key=data["api_key"], user_id=data["user_id"])

    @staticmethod
    def resend_verification(email: str, base_url: str = DEFAULT_BASE_URL) -> dict:
        """Resend verification email."""
        url = base_url.rstrip("/")
        with httpx.Client() as client:
            r = client.post(
                f"{url}/auth/resend-verification",
                json={"email": email},
            )
            r.raise_for_status()
            return r.json()

    @staticmethod
    def forgot_password(email: str, base_url: str = DEFAULT_BASE_URL) -> dict:
        """Request password reset. Sends email with reset link."""
        url = base_url.rstrip("/")
        with httpx.Client() as client:
            r = client.post(
                f"{url}/auth/forgot-password",
                json={"email": email},
            )
            r.raise_for_status()
            return r.json()

    @staticmethod
    def reset_password(token: str, new_password: str, base_url: str = DEFAULT_BASE_URL) -> dict:
        """Reset password using token from email link."""
        url = base_url.rstrip("/")
        with httpx.Client() as client:
            r = client.post(
                f"{url}/auth/reset-password",
                json={"token": token, "new_password": new_password},
            )
            r.raise_for_status()
            return r.json()

    @staticmethod
    def login(email: str, password: str, base_url: str = DEFAULT_BASE_URL) -> AuthResult:
        """Log in. Returns API key for X-API-Key header."""
        url = base_url.rstrip("/")
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                f"{url}/auth/login",
                json={"email": email, "password": password},
            )
            r.raise_for_status()
            data = r.json()
            return AuthResult(api_key=data["api_key"], user_id=data["user_id"])

    def deploy(
        self,
        model_id: str,
        model_path: str | None = None,
        config: dict[str, Any] | None = None,
        deployment_id: str | None = None,
    ) -> DeployResult:
        """Deploy a model. Pass deployment_id to update existing (creates new revision)."""
        payload: dict[str, Any] = {
            "model_id": model_id,
            "model_path": model_path,
            "config": config or {},
        }
        if deployment_id:
            payload["deployment_id"] = deployment_id
        with httpx.Client() as client:
            r = client.post(
                f"{self.base_url}/deploy",
                headers=self._headers(),
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return DeployResult(
                deployment_id=data["deployment_id"],
                status=data["status"],
                message=data.get("message", ""),
                revision=data.get("revision"),
            )

    def run(self, deployment_id: str, input_data: dict | list | Any) -> RunResult:
        """Run inference on a deployed model."""
        with httpx.Client() as client:
            r = client.post(
                f"{self.base_url}/run",
                headers=self._headers(),
                json={"deployment_id": deployment_id, "input": input_data},
            )
            r.raise_for_status()
            data = r.json()
            return RunResult(
                job_id=data["job_id"],
                status=data["status"],
                message=data.get("message", ""),
            )

    def status(self, resource_id: str) -> StatusResult:
        """Get status of a deployment or job."""
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/status/{resource_id}",
                headers=self._headers(),
            )
            r.raise_for_status()
            data = r.json()
            return StatusResult(
                id=data["id"],
                type=data["type"],
                status=data["status"],
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                error_message=data.get("error_message"),
                output_data=data.get("output_data"),
                tokens_used=data.get("tokens_used"),
                compute_seconds=data.get("compute_seconds"),
            )

    def list_deployments(self, limit: int = 50) -> list[dict[str, Any]]:
        """List deployments with revision counts."""
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/deployments",
                headers=self._headers(),
                params={"limit": limit},
            )
            r.raise_for_status()
            return r.json().get("deployments", [])

    def list_revisions(self, deployment_id: str) -> list[dict[str, Any]]:
        """List revisions for a deployment."""
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/deployments/{deployment_id}/revisions",
                headers=self._headers(),
            )
            r.raise_for_status()
            return r.json().get("revisions", [])

    def rollback(self, deployment_id: str, revision: int) -> dict[str, Any]:
        """Rollback deployment to a previous revision."""
        with httpx.Client() as client:
            r = client.post(
                f"{self.base_url}/deployments/{deployment_id}/rollback",
                headers=self._headers(),
                params={"revision": revision},
            )
            r.raise_for_status()
            return r.json()

    def list_api_keys(self) -> list[APIKeyInfo]:
        """List API keys for the current user."""
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/auth/api-keys",
                headers=self._headers(),
            )
            r.raise_for_status()
            data = r.json()
            return [
                APIKeyInfo(id=k["id"], name=k.get("name"), created_at=k["created_at"])
                for k in data["api_keys"]
            ]

    def create_api_key(self, name: str | None = None) -> CreateAPIKeyResult:
        """Create a new API key. The key is shown only once."""
        with httpx.Client() as client:
            r = client.post(
                f"{self.base_url}/auth/api-keys",
                headers=self._headers(),
                json={"name": name} if name else {},
            )
            r.raise_for_status()
            data = r.json()
            return CreateAPIKeyResult(
                api_key=data["api_key"],
                id=data["id"],
                name=data.get("name"),
            )

    def revoke_api_key(self, key_id: str) -> dict:
        """Revoke an API key."""
        with httpx.Client() as client:
            r = client.delete(
                f"{self.base_url}/auth/api-keys/{key_id}",
                headers=self._headers(),
            )
            r.raise_for_status()
            return r.json()

    def rotate_api_key(self) -> CreateAPIKeyResult:
        """Create a new API key and revoke the current one. Returns the new key."""
        with httpx.Client() as client:
            r = client.post(
                f"{self.base_url}/auth/api-keys/rotate",
                headers=self._headers(),
            )
            r.raise_for_status()
            data = r.json()
            return CreateAPIKeyResult(
                api_key=data["api_key"],
                id=data["id"],
                name=data.get("name"),
            )

    def usage(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> UsageResult:
        """Get usage stats for the authenticated user."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        with httpx.Client() as client:
            r = client.get(
                f"{self.base_url}/usage",
                headers=self._headers(),
                params=params if params else None,
            )
            r.raise_for_status()
            data = r.json()
            return UsageResult(
                user_id=data["user_id"],
                tokens_used=data["tokens_used"],
                compute_seconds=data["compute_seconds"],
                gpu_seconds=data.get("gpu_seconds", 0),
                job_count=data["job_count"],
                start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
                end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
                tokens_limit=data.get("tokens_limit"),
                compute_limit=data.get("compute_limit"),
                gpu_limit=data.get("gpu_limit"),
                gpu_seconds_overage=data.get("gpu_seconds_overage"),
            )
