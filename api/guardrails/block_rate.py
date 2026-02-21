"""Block rate limiting — prevent repeated blocked outputs from multiplying cost."""
import logging
from dataclasses import dataclass

from api.queue import get_redis

logger = logging.getLogger(__name__)

BLOCK_KEY_PREFIX = "guardrail:blocks"
DEFAULT_WINDOW_SECONDS = 300  # 5 min
DEFAULT_MAX_BLOCKS = 5
DEFAULT_RETRY_AFTER_SECONDS = 60


def _block_key(user_id: str, deployment_id: str) -> str:
    return f"{BLOCK_KEY_PREFIX}:{user_id}:{deployment_id}"


@dataclass
class BlockRateResult:
    """Result of block rate limit check."""
    within_limit: bool
    retry_after_seconds: int
    blocks_in_window: int = 0
    max_blocks: int = 0


async def check_block_rate_limit(
    user_id: str,
    deployment_id: str,
    max_blocks: int | None = None,
    window_seconds: int | None = None,
) -> BlockRateResult:
    """
    Check if user has exceeded block rate limit.
    Returns BlockRateResult with within_limit, retry_after_seconds, blocks_in_window, max_blocks.
    """
    max_blocks = max_blocks or DEFAULT_MAX_BLOCKS
    window_seconds = window_seconds or DEFAULT_WINDOW_SECONDS
    try:
        redis = await get_redis()
        try:
            key = _block_key(user_id, deployment_id)
            count = await redis.get(key)
            if count is None:
                return BlockRateResult(True, 0, 0, max_blocks)
            n = int(count)
            if n >= max_blocks:
                ttl = await redis.ttl(key)
                retry = max(ttl, DEFAULT_RETRY_AFTER_SECONDS) if ttl > 0 else DEFAULT_RETRY_AFTER_SECONDS
                return BlockRateResult(False, retry, n, max_blocks)
            return BlockRateResult(True, 0, n, max_blocks)
        finally:
            await redis.aclose()
    except Exception as e:
        logger.warning("Block rate check failed, allowing: %s", e)
        return BlockRateResult(True, 0, 0, max_blocks)


async def increment_block_count(
    user_id: str,
    deployment_id: str,
    window_seconds: int | None = None,
) -> int:
    """Increment block count for user+deployment. Returns new count."""
    window_seconds = window_seconds or DEFAULT_WINDOW_SECONDS
    try:
        redis = await get_redis()
        try:
            key = _block_key(user_id, deployment_id)
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            return int(results[0])
        finally:
            await redis.aclose()
    except Exception as e:
        logger.warning("Block count increment failed: %s", e)
        return 0
