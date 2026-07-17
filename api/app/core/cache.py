from __future__ import annotations

import functools
import hashlib
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])

_redis: redis.Redis | None = None
_redis_available: bool = False


async def _ensure_redis() -> bool:
    global _redis, _redis_available
    if _redis is not None:
        return _redis_available
    try:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis.ping()
        _redis_available = True
    except Exception:
        _redis_available = False
        logger.debug("Redis cache unavailable")
    return _redis_available


def _cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"cache:{prefix}:{digest}"


def cached(prefix: str, ttl: int = 30):
    """Decorator that caches async function results in Redis with a TTL.

    If Redis is unavailable, the function executes normally (cache bypass).
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not await _ensure_redis():
                return await func(*args, **kwargs)

            key = _cache_key(prefix, *args, **kwargs)
            try:
                cached_value = await _redis.get(key)  # type: ignore[union-attr]
                if cached_value is not None:
                    return json.loads(cached_value)
            except Exception:
                logger.debug("Cache read error, bypassing")

            result = await func(*args, **kwargs)
            try:
                await _redis.set(key, json.dumps(result, default=str), ex=ttl)  # type: ignore[union-attr]
            except Exception:
                logger.debug("Cache write error, skipping")
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


async def invalidate_prefix(prefix: str) -> None:
    """Remove all cache entries with a given prefix."""
    if not await _ensure_redis():
        return
    cursor = 0
    pattern = f"cache:{prefix}:*"
    while True:
        cursor, keys = await _redis.scan(cursor, match=pattern, count=100)  # type: ignore[union-attr]
        if keys:
            await _redis.delete(*keys)  # type: ignore[union-attr]
        if cursor == 0:
            break
