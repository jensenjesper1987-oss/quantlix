"""Request-level scoring — 0–1 score per inference based on input/output and policies."""
from api.scoring.scorer import compute_score

__all__ = ["compute_score"]
