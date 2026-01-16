"""Caching Utilities"""

import hashlib
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from function arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create a stable string representation of arguments
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_response(
    prefix: str,
    ttl: int = 3600,
    skip_cache: Optional[Callable] = None
):
    """
    Decorator to cache function responses in Redis.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 1 hour)
        skip_cache: Optional function to determine if cache should be skipped
        
    Usage:
        @cache_response("api:requirement", ttl=1800)
        async def analyze_requirement(text: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if we should skip cache
            if skip_cache and skip_cache(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            try:
                # Try to get from cache
                redis = await get_redis()
                cached_value = await redis.get(cache_key)
                
                if cached_value:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_value)
                
                # Cache miss - call function
                logger.debug(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Store in cache
                await redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
                
                return result
                
            except Exception as e:
                # If cache fails, just call the function
                logger.warning(f"Cache error: {e}. Calling function directly.")
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def invalidate_cache(prefix: str, *args, **kwargs):
    """
    Invalidate cache for specific key.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    cache_key = generate_cache_key(prefix, *args, **kwargs)
    
    try:
        redis = await get_redis()
        await redis.delete(cache_key)
        logger.debug(f"Cache invalidated: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache: {e}")


async def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys matching pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "api:requirement:*")
    """
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        
        if keys:
            await redis.delete(*keys)
            logger.debug(f"Invalidated {len(keys)} cache keys matching: {pattern}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache pattern: {e}")


async def get_cached(key: str) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None
    """
    try:
        redis = await get_redis()
        cached_value = await redis.get(key)
        
        if cached_value:
            return json.loads(cached_value)
        
        return None
    except Exception as e:
        logger.warning(f"Failed to get cached value: {e}")
        return None


async def set_cached(key: str, value: Any, ttl: int = 3600):
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds
    """
    try:
        redis = await get_redis()
        await redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    except Exception as e:
        logger.warning(f"Failed to set cached value: {e}")
