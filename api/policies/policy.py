"""Orchestration policy — decide action based on score and config."""
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyAction(str, Enum):
    """Action to take based on policy evaluation."""
    ALLOW = "allow"
    BLOCK = "block"
    LOG = "log"  # Allow but log for review


@dataclass
class PolicyConfig:
    """Config for orchestration policy."""
    block_threshold: float = 0.3   # Block if score < this
    log_threshold: float = 0.7     # Log if score < this (but allow)
    # Future: route_to_model: str | None = None


def apply_policy(
    score: float,
    config: PolicyConfig | None = None,
) -> tuple[PolicyAction, str]:
    """
    Apply orchestration policy based on score.
    Returns (action, reason).
    """
    cfg = config or PolicyConfig()

    if score < cfg.block_threshold:
        return PolicyAction.BLOCK, f"Score {score:.2f} below block threshold {cfg.block_threshold}"
    if score < cfg.log_threshold:
        logger.warning("Policy: logging request with score %.2f (below log threshold %.2f)", score, cfg.log_threshold)
        return PolicyAction.LOG, f"Score {score:.2f} below log threshold {cfg.log_threshold}"
    return PolicyAction.ALLOW, ""
