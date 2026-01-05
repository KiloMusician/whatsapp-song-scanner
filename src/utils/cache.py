"""Caching mechanisms using Redis."""
import redis
import json
from typing import Any, Optional
from config.settings import REDIS_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Redis-based cache manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_CONFIG['host'],
                port=REDIS_CONFIG['port'],
                db=REDIS_CONFIG['db'],
                password=REDIS_CONFIG['password'] if REDIS_CONFIG['password'] else None,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connection established")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
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
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: int = None):
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
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    def delete(self, key: str):
        """Delete value from cache.
        
        Args:
            key: Cache key
        """
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
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
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False
    
    def flush_all(self):
        """Flush all cache entries (use with caution)."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.flushdb()
            logger.warning("All cache entries flushed")
        except Exception as e:
            logger.error(f"Cache flush error: {e}")

# SINGLETON INSTANCE
cache_manager = CacheManager()
