"""
Redis connection and caching utilities
"""
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
import asyncio

try:
    import redis
    from redis.exceptions import ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    RedisConnectionError = Exception

from app.core.config import settings
from app.core.logger import logger


class RedisClient:
    """Redis client wrapper with connection pooling and error handling"""
    
    def __init__(self):
        self._sync_client: Optional[Any] = None
        self._connection_pool: Optional[Any] = None
        
    def get_sync_client(self) -> Optional[Any]:
        """Get synchronous Redis client"""
        # Check if Redis package is available
        if not REDIS_AVAILABLE:
            logger.warning("Redis package not installed. Caching will be disabled.")
            return None
            
        # Check if caching is enabled
        if not settings.CACHE_ENABLED:
            logger.info("Caching is disabled via CACHE_ENABLED=False")
            return None
            
        if self._sync_client is None:
            try:
                if not self._connection_pool:
                    self._connection_pool = redis.ConnectionPool.from_url(
                        settings.REDIS_CONNECTION_URL,
                        decode_responses=True,
                        max_connections=20
                    )
                
                self._sync_client = redis.Redis(connection_pool=self._connection_pool)
                # Test connection
                self._sync_client.ping()
                logger.info("Redis sync client connected successfully")
            except RedisConnectionError as e:
                logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
                self._sync_client = None
            except Exception as e:
                logger.warning(f"Redis connection error: {e}. Caching will be disabled.")
                self._sync_client = None
        
        return self._sync_client
    
    def close_connections(self):
        """Close Redis connections"""
        if self._sync_client:
            self._sync_client.close()
        if self._connection_pool:
            self._connection_pool.disconnect()


# Global Redis client instance
redis_client = RedisClient()


class CacheService:
    """Service for caching operations with automatic serialization"""
    
    def __init__(self):
        self.client = redis_client
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        try:
            # Try JSON first for simple types
            return json.dumps(value)
        except (TypeError, ValueError):
            # Use pickle for complex objects that can't be JSON serialized
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str, use_pickle: bool = False) -> Any:
        """Deserialize value from Redis storage"""
        if use_pickle:
            return pickle.loads(bytes.fromhex(value))
        else:
            return json.loads(value)
    
    def set(self, key: str, value: Any, ttl: int = None, use_pickle: bool = False) -> bool:
        """
        Set a value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (defaults to CACHE_TTL_SECONDS)
            use_pickle: Use pickle for serialization (for complex objects)
        """
        client = self.client.get_sync_client()
        if not client:
            return False
        
        try:
            if use_pickle:
                serialized_value = pickle.dumps(value).hex()
                cache_key = f"pickle:{key}"
            else:
                try:
                    # Try JSON serialization first
                    serialized_value = json.dumps(value)
                    cache_key = key
                except (TypeError, ValueError):
                    # Fall back to pickle for complex objects
                    serialized_value = pickle.dumps(value).hex()
                    cache_key = f"pickle:{key}"
            
            ttl = ttl or settings.CACHE_TTL_SECONDS
            result = client.setex(cache_key, ttl, serialized_value)
            logger.debug(f"Cached key: {cache_key} with TTL: {ttl}")
            return result
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def get(self, key: str, use_pickle: bool = False) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
            use_pickle: Use pickle for deserialization
        """
        client = self.client.get_sync_client()
        if not client:
            return None
        
        try:
            # Try both regular key and pickle key
            value = None
            cache_key = key
            
            if use_pickle:
                cache_key = f"pickle:{key}"
                value = client.get(cache_key)
            else:
                # Try regular key first
                value = client.get(key)
                # If not found, try pickle key
                if value is None:
                    pickle_key = f"pickle:{key}"
                    value = client.get(pickle_key)
                    if value is not None:
                        use_pickle = True
                        cache_key = pickle_key
            
            if value is None:
                return None
            
            if use_pickle or cache_key.startswith("pickle:"):
                return pickle.loads(bytes.fromhex(value))
            else:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        client = self.client.get_sync_client()
        if not client:
            return False
        
        try:
            # Delete both regular and pickle versions
            result = client.delete(key, f"pickle:{key}")
            logger.debug(f"Deleted cache key: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        client = self.client.get_sync_client()
        if not client:
            return 0
        
        try:
            keys = client.keys(pattern)
            if keys:
                result = client.delete(*keys)
                logger.debug(f"Deleted {result} keys matching pattern: {pattern}")
                return result
            return 0
        except Exception as e:
            logger.error(f"Failed to delete keys with pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        client = self.client.get_sync_client()
        if not client:
            return False
        
        try:
            return client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL of a key (-1 if no expiry, -2 if key doesn't exist)"""
        client = self.client.get_sync_client()
        if not client:
            return -2
        
        try:
            return client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -2


# Global cache service instance
cache = CacheService()


def cache_result(key_prefix: str, ttl: int = None, use_pickle: bool = False):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        use_pickle: Use pickle for complex objects
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If caching is disabled, just execute the function
            if not settings.CACHE_ENABLED:
                logger.debug(f"Cache disabled - executing function directly: {func.__name__}")
                return func(*args, **kwargs)
            
            # Generate cache key from function args
            key_parts = [key_prefix]
            
            # Add positional args to key
            for arg in args:
                if hasattr(arg, 'id'):  # For objects with id (like User)
                    key_parts.append(str(arg.id))
                else:
                    key_parts.append(str(arg))
            
            # Add keyword args to key
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache first
            cached_result = cache.get(cache_key, use_pickle=use_pickle)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl, use_pickle=use_pickle)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """Invalidate all cache keys matching a pattern"""
    if not settings.CACHE_ENABLED:
        logger.debug("Cache disabled - skipping cache invalidation")
        return 0
    return cache.delete_pattern(pattern)


def get_cache_info() -> dict:
    """Get cache statistics and info"""
    if not settings.CACHE_ENABLED:
        return {"status": "disabled", "message": "Caching is disabled via CACHE_ENABLED=False"}
        
    if not REDIS_AVAILABLE:
        return {"status": "unavailable", "message": "Redis package not installed"}
    
    client = redis_client.get_sync_client()
    if not client:
        return {"status": "disconnected"}
    
    try:
        info = client.info()
        return {
            "status": "connected",
            "redis_version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    except Exception as e:
        logger.error(f"Failed to get cache info: {e}")
        return {"status": "error", "error": str(e)}
