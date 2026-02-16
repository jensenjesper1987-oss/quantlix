"""Redis queue for inference jobs."""
import json
from typing import Any

from redis.asyncio import Redis

from api.config import settings

INFERENCE_QUEUE = "inference:queue"


async def get_redis() -> Redis:
    """Get Redis connection. Caller must close or use as context manager."""
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def enqueue_job(job_id: str, payload: dict[str, Any]) -> None:
    """Push inference job to Redis queue."""
    redis = await get_redis()
    try:
        await redis.rpush(INFERENCE_QUEUE, json.dumps({"job_id": job_id, **payload}))
    finally:
        await redis.aclose()
