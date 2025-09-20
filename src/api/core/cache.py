"""
FastAPI Cache Module
Provides cache client and lifecycle management for the FastAPI application
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

try:
    from api.core.config import settings
except ImportError:
    # Fallback settings when dependencies are not available
    class FallbackSettings:
        CACHE_ENABLED = False
        redis_url = "redis://localhost:6379/0"

    settings = FallbackSettings()

# Try to import Redis, fall back to None if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis as redis
        REDIS_AVAILABLE = True
    except ImportError:
        redis = None
        REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global cache client
_cache_client = None
_cache_pool = None


class CacheClient:
    """
    Redis cache client wrapper that provides the interface expected by middleware
    """

    def __init__(self, redis_client):
        self._redis = redis_client

    def pipeline(self):
        """Create a Redis pipeline for batch operations"""
        return self._redis.pipeline()

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration"""
        try:
            return await self._redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> int:
        """Delete key from cache"""
        try:
            return await self._redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            return await self._redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache ttl error for key {key}: {e}")
            return -1

    # Additional methods needed by rate limiting middleware
    async def zremrangebyscore(self, name: str, min_score: float, max_score: float) -> int:
        """Remove members from sorted set by score range"""
        try:
            return await self._redis.zremrangebyscore(name, min_score, max_score)
        except Exception as e:
            logger.error(f"Cache zremrangebyscore error for {name}: {e}")
            return 0

    async def zadd(self, name: str, mapping: dict) -> int:
        """Add members to sorted set"""
        try:
            return await self._redis.zadd(name, mapping)
        except Exception as e:
            logger.error(f"Cache zadd error for {name}: {e}")
            return 0

    async def zcount(self, name: str, min_score: float, max_score: float) -> int:
        """Count members in sorted set by score range"""
        try:
            return await self._redis.zcount(name, min_score, max_score)
        except Exception as e:
            logger.error(f"Cache zcount error for {name}: {e}")
            return 0


class CachePipeline:
    """
    Redis pipeline wrapper that provides the interface expected by middleware
    """

    def __init__(self, redis_pipeline):
        self._pipeline = redis_pipeline

    def zremrangebyscore(self, name: str, min_score: float, max_score: float):
        """Remove members from sorted set by score range"""
        return self._pipeline.zremrangebyscore(name, min_score, max_score)

    def zadd(self, name: str, mapping: dict):
        """Add members to sorted set"""
        return self._pipeline.zadd(name, mapping)

    def zcount(self, name: str, min_score: float, max_score: float):
        """Count members in sorted set by score range"""
        return self._pipeline.zcount(name, min_score, max_score)

    def expire(self, name: str, time: int):
        """Set expiration for key"""
        return self._pipeline.expire(name, time)

    async def execute(self):
        """Execute pipeline commands"""
        try:
            return await self._pipeline.execute()
        except Exception as e:
            logger.error(f"Cache pipeline execute error: {e}")
            return []


# Monkey patch the CacheClient pipeline method to return our wrapper
def _create_cache_pipeline(self):
    """Create a wrapped pipeline"""
    return CachePipeline(self._redis.pipeline())

CacheClient.pipeline = _create_cache_pipeline


async def init_cache() -> bool:
    """
    Initialize Redis cache connection

    Returns:
        bool: True if cache was successfully initialized, False otherwise
    """
    global _cache_client, _cache_pool

    if not settings.CACHE_ENABLED:
        logger.info("Cache is disabled in configuration")
        return False

    if not REDIS_AVAILABLE:
        logger.warning("Redis module not available - cache will be disabled")
        return False

    try:
        # Create connection pool
        _cache_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30
        )

        # Create Redis client
        redis_client = redis.Redis(
            connection_pool=_cache_pool,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test connection
        await redis_client.ping()

        # Wrap in our cache client
        _cache_client = CacheClient(redis_client)

        logger.info(f"Cache initialized successfully: {settings.redis_url}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        _cache_client = None
        _cache_pool = None
        return False


async def close_cache():
    """
    Close Redis cache connection
    """
    global _cache_client, _cache_pool

    if _cache_client:
        try:
            # Close the underlying Redis connection
            if hasattr(_cache_client._redis, 'close'):
                await _cache_client._redis.close()

            # Wait for the connection to close
            if hasattr(_cache_client._redis, 'wait_closed'):
                await _cache_client._redis.wait_closed()

            _cache_client = None
            logger.info("Cache connection closed")

        except Exception as e:
            logger.error(f"Error closing cache connection: {e}")

    if _cache_pool:
        try:
            await _cache_pool.disconnect()
            _cache_pool = None
            logger.info("Cache pool disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting cache pool: {e}")


def get_cache_client() -> Optional[CacheClient]:
    """
    Get the current cache client instance

    Returns:
        CacheClient: Current cache client or None if not initialized
    """
    return _cache_client


def is_cache_available() -> bool:
    """
    Check if cache is available and ready to use

    Returns:
        bool: True if cache is available, False otherwise
    """
    return _cache_client is not None


@asynccontextmanager
async def cache_context():
    """
    Context manager for cache operations
    Ensures cache is initialized and cleaned up properly
    """
    cache_was_initialized = await init_cache()
    try:
        yield get_cache_client()
    finally:
        if cache_was_initialized:
            await close_cache()


# Health check function
async def get_cache_health() -> dict:
    """
    Get cache health status

    Returns:
        dict: Health status information
    """
    if not REDIS_AVAILABLE:
        return {
            "status": "disabled",
            "error": "Redis module not available",
            "redis_info": None
        }

    if not _cache_client:
        return {
            "status": "disabled",
            "error": "Cache not initialized",
            "redis_info": None
        }

    try:
        # Test basic operations
        test_key = "health_check_test"
        await _cache_client.set(test_key, "test_value", ex=1)
        value = await _cache_client.get(test_key)
        await _cache_client.delete(test_key)

        if value != "test_value":
            return {
                "status": "error",
                "error": "Cache read/write test failed",
                "redis_info": None
            }

        # Get Redis info
        redis_info = await _cache_client._redis.info()

        return {
            "status": "healthy",
            "error": None,
            "redis_info": {
                "version": redis_info.get("redis_version"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory": redis_info.get("used_memory_human"),
                "uptime": redis_info.get("uptime_in_seconds")
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "redis_info": None
        }


# Export main functions
__all__ = [
    "init_cache",
    "close_cache",
    "get_cache_client",
    "is_cache_available",
    "cache_context",
    "get_cache_health",
    "CacheClient"
]