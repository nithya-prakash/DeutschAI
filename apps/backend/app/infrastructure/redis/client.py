"""Redis client factory.

Used for rate limiting hooks and backs the planner cache; a candidate for
background job queues as the platform grows.
"""
from functools import lru_cache

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_redis_client() -> redis.Redis:
    return redis.from_url(str(settings.REDIS_URI), decode_responses=True)
