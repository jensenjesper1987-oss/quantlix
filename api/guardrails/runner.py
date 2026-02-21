"""Run guardrails on input or output."""
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from api.guardrails.base import GuardrailAction, GuardrailResult
from api.guardrails.metrics import (
    guardrail_blocked_total,
    guardrail_errors_total,
    guardrail_flagged_total,
    guardrail_timeouts_total,
)
from api.guardrails.rules import BUILTIN_RULES

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)


def _apply_rule_overrides(
    results: list[GuardrailResult],
    rule_config: dict[str, dict] | None,
) -> list[GuardrailResult]:
    """Apply per-deployment rule overrides (e.g. upgrade FLAG to BLOCK)."""
    if not rule_config:
        return results
    out: list[GuardrailResult] = []
    for r in results:
        cfg = rule_config.get(r.rule_name)
        if cfg and isinstance(cfg, dict) and cfg.get("action") == "block":
            if r.action == GuardrailAction.FLAG:
                r = GuardrailResult(
                    passed=False,
                    action=GuardrailAction.BLOCK,
                    rule_name=r.rule_name,
                    message=r.message,
                    details=r.details,
                )
        out.append(r)
    return out if out else results


def run_guardrails(
    data: str | dict,
    phase: str,
    enabled_rules: list[str] | dict | None = None,
    rule_config: dict[str, dict] | None = None,
    timeout_seconds: float | None = None,
    fail_open: bool = True,
) -> tuple[bool, list[GuardrailResult]]:
    """
    Run guardrails on input or output.
    - enabled_rules: list of rule names, or dict {"pii": {}, "safety": {}} for per-rule config
    - rule_config: per-rule overrides, e.g. {"pii": {"action": "block"}}
    - timeout_seconds: max time for all rules; default from config
    - fail_open: if True, allow on error/timeout; if False, block
    Returns (passed, results). passed=False if any rule blocks.
    """
    from api.config import settings

    timeout = timeout_seconds if timeout_seconds is not None else settings.guardrail_timeout_seconds

    # Parse enabled_rules: list or dict
    if enabled_rules is None:
        enabled = {r.name for r in BUILTIN_RULES}
        merged_rule_config = rule_config
    elif isinstance(enabled_rules, list):
        enabled = set(enabled_rules)
        merged_rule_config = rule_config
    else:
        enabled = set(enabled_rules.keys())
        merged_rule_config = {**(rule_config or {}), **enabled_rules}

    rules_to_run = [
        r for r in BUILTIN_RULES
        if r.name in enabled and (r.phase == "both" or r.phase == phase)
    ]

    results: list[GuardrailResult] = []
    try:
        futures = {
            _executor.submit(r.check, data): r
            for r in rules_to_run
        }
        import concurrent.futures as cf
        done, not_done = cf.wait(futures.keys(), timeout=timeout)

        if not_done:
            guardrail_timeouts_total.inc()
            logger.warning("Guardrail timeout after %.1fs (%d rules pending)", timeout, len(not_done))
            for f in not_done:
                f.cancel()
            if not fail_open:
                return False, [GuardrailResult(False, GuardrailAction.BLOCK, "timeout", "Guardrail timeout", {})]
            return True, []

        for fut in done:
            try:
                result = fut.result()
                results.append(result)
            except Exception as e:
                guardrail_errors_total.inc()
                logger.exception("Guardrail %s failed: %s", futures[fut].name, e)
                if not fail_open:
                    return False, [GuardrailResult(False, GuardrailAction.BLOCK, "error", str(e), {})]
                # fail_open: skip this rule

        results = _apply_rule_overrides(results, merged_rule_config)
        for r in results:
            if r.action == GuardrailAction.FLAG:
                guardrail_flagged_total.labels(rule=r.rule_name).inc()
            if r.action == GuardrailAction.BLOCK:
                guardrail_blocked_total.labels(rule=r.rule_name).inc()
                return False, results
        return True, results

    except Exception as e:
        guardrail_errors_total.inc()
        logger.exception("Guardrail runner failed: %s", e)
        if not fail_open:
            return False, [GuardrailResult(False, GuardrailAction.BLOCK, "error", str(e), {})]
        return True, []
