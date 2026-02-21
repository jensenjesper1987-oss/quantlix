"""Guardrail config parsing from deployment.config."""
from api.config import settings


def get_guardrail_config(deployment) -> tuple[list | dict | None, dict | None, bool, float | None]:
    """
    Extract guardrail config from deployment.config.
    Returns (enabled_rules, rule_config, fail_open, timeout_seconds).
    """
    cfg = deployment.config or {}
    gr = cfg.get("guardrails")
    rule_config = gr if isinstance(gr, dict) else None
    enabled_rules = gr
    fail_open = cfg.get("guardrail_fail_open", settings.guardrail_fail_open)
    timeout = cfg.get("guardrail_timeout") or settings.guardrail_timeout_seconds
    return enabled_rules, rule_config, fail_open, timeout
