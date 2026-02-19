"""Public demo endpoint — no auth required. Returns sample inference output."""
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.rate_limit import rate_limit_demo

router = APIRouter()


class DemoInput(BaseModel):
    """Optional input for demo. If omitted, uses default prompt."""
    prompt: str = "Hello, world!"


class DemoResponse(BaseModel):
    """Same format as inference output (what /run jobs return)."""
    output_data: dict
    tokens_used: int
    compute_seconds: float


@router.post("", response_model=DemoResponse)
async def demo(
    _: Annotated[None, Depends(rate_limit_demo)] = None,
    body: DemoInput | None = None,
) -> DemoResponse:
    """
    Public demo — no API key required.
    Returns a sample inference response in the same format as the real /run API.
    Rate limited to 20 requests/hour per IP.
    """
    prompt = body.prompt if body else "Hello, world!"
    # Simulate inference output (matches qx-example / DistilGPT2 format)
    generated = f"{prompt[:200]} — powered by Quantlix."
    tokens = min(len(generated.split()) * 2, 99)
    return DemoResponse(
        output_data={
            "generated": generated,
            "model": "qx-example",
        },
        tokens_used=tokens,
        compute_seconds=0.04,
    )
