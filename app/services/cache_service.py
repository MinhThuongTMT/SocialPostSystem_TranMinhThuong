import json
from typing import Optional, Any
from datetime import timedelta
from app.config.redis_config import get_redis


class CacheService:
    """Service for Redis caching operations"""

    @staticmethod
    async def get_redis():
        return await get_redis()

    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration time"""
        try:
            redis = await self.get_redis()
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, default=str)
            await redis.setex(key, expire, value)
            return True
        except Exception as e:
            print(f"Cache set error: {str(e)}")
            return False

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis = await self.get_redis()
            value = await redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            print(f"Cache get error: {str(e)}")
            return None

    async def delete_cache(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis = await self.get_redis()
            await redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {str(e)}")
            return False

    async def clear_cache(self, pattern: str = "*") -> bool:
        """Clear cache by pattern"""
        try:
            redis = await self.get_redis()
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear error: {str(e)}")
            return False

    async def publish_event(self, channel: str, message: Any) -> int:
        """Publish event to Redis Pub/Sub"""
        try:
            redis = await self.get_redis()
            if isinstance(message, dict):
                message = json.dumps(message, default=str)
            subscribers = await redis.publish(channel, message)
            return subscribers
        except Exception as e:
            print(f"Publish error: {str(e)}")
            return 0


# Cache key patterns
CACHE_KEYS = {
    "posts": "posts:{page}",
    "post": "post:{post_id}",
    "user": "user:{user_id}",
    "user_posts": "user_posts:{user_id}:{page}",
    "feed": "feed:{user_id}:{page}",
    "trending_posts": "trending_posts:{page}"
}
