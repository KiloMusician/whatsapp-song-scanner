"""Caching mechanisms using Redis."""

import redis
from typing import Optional, cast
from config.settings import REDIS_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_CONFIG["host"],
                port=REDIS_CONFIG["port"],
                db=REDIS_CONFIG["db"],
                password=REDIS_CONFIG["password"] if REDIS_CONFIG["password"] else None,
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connection established")
        except redis.ConnectionError as exc:
            logger.error("Redis connection failed: %s", exc)
            self.redis_client = None

    def get(self, key: str) -> Optional[str]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis_client:
            return None

        try:
            return cast(Optional[str], self.redis_client.get(key))
        except redis.RedisError as exc:
            logger.error("Cache get error for key %s: %s", key, exc)
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        if not self.redis_client:
            return

        try:
            if ttl:
                self.redis_client.setex(key, ttl, value)
            else:
                self.redis_client.set(key, value)
        except redis.RedisError as exc:
            logger.error("Cache set error for key %s: %s", key, exc)

    def delete(self, key: str):
        """Delete value from cache.

        Args:
            key: Cache key
        """
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(key)
        except redis.RedisError as exc:
            logger.error("Cache delete error for key %s: %s", key, exc)

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as exc:
            logger.error("Cache exists check error for key %s: %s", key, exc)
            return False

    def flush_all(self):
        """Flush all cache entries (use with caution)."""
        if not self.redis_client:
            return

        try:
            self.redis_client.flushdb()
            logger.warning("All cache entries flushed")
        except redis.RedisError as exc:
            logger.error("Cache flush error: %s", exc)


# SINGLETON INSTANCE
cache_manager = CacheManager()
