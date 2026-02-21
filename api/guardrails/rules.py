"""Built-in guardrail rules: PII, safety, content."""
import re
from typing import Any

from api.guardrails.base import GuardrailAction, GuardrailResult, GuardrailRule


def _extract_text(data: str | dict) -> str:
    """Extract searchable text from input/output."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        parts = []
        for k, v in data.items():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, dict):
                parts.append(_extract_text(v))
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict):
                        parts.append(_extract_text(item))
        return " ".join(parts)
    return str(data)


# PII patterns (simple regex; extend with more patterns)
PII_PATTERNS = [
    (r"\b\d{16}\b", "credit_card"),
    (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "credit_card"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{10,}\b", "phone_or_id"),
]


def pii_guardrail(data: str | dict) -> GuardrailResult:
    """Detect PII in text. Flags but does not block by default."""
    text = _extract_text(data)
    found = []
    for pattern, label in PII_PATTERNS:
        if re.search(pattern, text):
            found.append(label)
    if found:
        return GuardrailResult(
            passed=False,
            action=GuardrailAction.FLAG,
            rule_name="pii",
            message=f"Possible PII detected: {', '.join(set(found))}",
            details={"types": list(set(found))},
        )
    return GuardrailResult(
        passed=True,
        action=GuardrailAction.ALLOW,
        rule_name="pii",
    )


# Safety blocklist (harmful content)
SAFETY_BLOCKLIST = [
    r"how to (build|make|create) (a )?bomb",
    r"how to (build|make|create) (a )?weapon",
    r"kill (yourself|myself)",
    r"self[\s-]?harm",
    r"suicide",
]


def safety_guardrail(data: str | dict) -> GuardrailResult:
    """Block harmful content."""
    text = _extract_text(data).lower()
    for pattern in SAFETY_BLOCKLIST:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(
                passed=False,
                action=GuardrailAction.BLOCK,
                rule_name="safety",
                message="Content violates safety policy",
                details={"pattern": pattern},
            )
    return GuardrailResult(
        passed=True,
        action=GuardrailAction.ALLOW,
        rule_name="safety",
    )


# Content policy (e.g., prompt injection attempts)
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"disregard (all )?(previous|above)",
    r"you are now",
    r"new instructions:",
    r"system:",
    r"\[INST\]",
]


def content_guardrail(data: str | dict) -> GuardrailResult:
    """Detect prompt injection / policy violations. Flags by default."""
    text = _extract_text(data)
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(
                passed=False,
                action=GuardrailAction.FLAG,
                rule_name="content",
                message="Possible prompt injection detected",
                details={"pattern": pattern},
            )
    return GuardrailResult(
        passed=True,
        action=GuardrailAction.ALLOW,
        rule_name="content",
    )


# Built-in rules (can be enabled/disabled via config)
BUILTIN_RULES: list[GuardrailRule] = [
    GuardrailRule("pii", pii_guardrail, "both"),
    GuardrailRule("safety", safety_guardrail, "both"),
    GuardrailRule("content", content_guardrail, "input"),
]
