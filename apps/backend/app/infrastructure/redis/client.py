"""Redis client factory.

Used today for rate limiting hooks; from Phase 2 onward also backs
background job queues and planner/session caching.
"""
from functools import lru_cache

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_redis_client() -> redis.Redis:
    return redis.from_url(str(settings.REDIS_URI), decode_responses=True)
