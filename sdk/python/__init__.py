"""Python SDK for Quantlix (deprecated — use sdk.quantlix)."""

from sdk.quantlix import (
    AuthResult,
    DEFAULT_BASE_URL,
    DeployResult,
    QuantlixCloudClient,
    RunResult,
    StatusResult,
    UsageResult,
)

# Backward compatibility
CloudClient = QuantlixCloudClient

__all__ = [
    "AuthResult",
    "CloudClient",
    "DeployResult",
    "RunResult",
    "StatusResult",
    "UsageResult",
    "DEFAULT_BASE_URL",
]
