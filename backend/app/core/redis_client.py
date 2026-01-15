"""Redis Client Management"""

import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,
    )


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    return redis_client
