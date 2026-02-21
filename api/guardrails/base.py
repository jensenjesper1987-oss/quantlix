"""Base types for guardrails."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class GuardrailAction(str, Enum):
    """Action taken by a guardrail."""
    ALLOW = "allow"
    FLAG = "flag"   # Log but allow
    BLOCK = "block"


@dataclass
class GuardrailResult:
    """Result of running guardrails on input or output."""
    passed: bool
    action: GuardrailAction
    rule_name: str
    message: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class GuardrailRule:
    """A single guardrail rule."""
    name: str
    check: Callable[[str | dict], GuardrailResult]
    phase: str = "both"  # "input", "output", or "both"
