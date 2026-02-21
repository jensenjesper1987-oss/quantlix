"""Compute 0–1 score for a request based on input, output, and guardrail results."""
from api.guardrails.base import GuardrailAction, GuardrailResult


def compute_score(
    input_data: dict | None,
    output_data: dict | None,
    guardrail_results_input: list[GuardrailResult],
    guardrail_results_output: list[GuardrailResult],
) -> float:
    """
    Compute a single 0–1 score for the request.
    - 1.0 = perfect (no flags, no blocks)
    - Lower when guardrails flag or block
    """
    score = 1.0

    for r in guardrail_results_input + guardrail_results_output:
        if r.action == GuardrailAction.BLOCK:
            return 0.0
        if r.action == GuardrailAction.FLAG:
            score -= 0.2  # Each flag reduces score

    return max(0.0, min(1.0, score))
