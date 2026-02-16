"""
Inference client — Call inference HTTP API (mock mode) or read result from Redis (K8s mode).
"""
import json
from typing import Any

import httpx

from orchestrator.config import settings


async def call_inference_http(job_id: str, input_data: dict) -> dict | None:
    """Call inference HTTP API. Returns {output_data, tokens_used, compute_seconds} or None."""
    if not settings.inference_url or not settings.inference_url.strip():
        return None
    url = settings.inference_url.rstrip("/") + "/run"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, json={"job_id": job_id, "input": input_data})
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


async def read_inference_result_from_redis(job_id: str) -> dict | None:
    """Read inference result from Redis (written by K8s Job container)."""
    try:
        from redis.asyncio import Redis

        r = Redis.from_url(settings.redis_url, decode_responses=True)
        raw = await r.get(f"inference:result:{job_id}")
        await r.aclose()
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None
