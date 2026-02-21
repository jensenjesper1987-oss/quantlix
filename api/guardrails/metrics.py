"""Prometheus metrics for guardrails."""
from prometheus_client import Counter

guardrail_blocked_total = Counter(
    "quantlix_guardrail_blocked_total",
    "Total requests blocked by guardrails",
    ["rule"],
)
guardrail_flagged_total = Counter(
    "quantlix_guardrail_flagged_total",
    "Total requests flagged (but allowed) by guardrails",
    ["rule"],
)
guardrail_errors_total = Counter(
    "quantlix_guardrail_errors_total",
    "Total guardrail execution errors",
)
guardrail_timeouts_total = Counter(
    "quantlix_guardrail_timeouts_total",
    "Total guardrail timeouts",
)
