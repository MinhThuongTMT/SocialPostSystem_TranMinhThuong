import redis.asyncio as aioredis
from typing import Optional
from app.config.settings import settings

class RedisConnection:
    """Redis connection handler"""
    
    redis: Optional[aioredis.Redis] = None

async def connect_to_redis():
    """Initialize Redis connection"""
    RedisConnection.redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    await RedisConnection.redis.ping()
    print("✅ Connected to Redis")

async def close_redis_connection():
    """Close Redis connection"""
    if RedisConnection.redis:
        await RedisConnection.redis.close()
        print("✅ Closed Redis connection")

async def get_redis():
    """Get Redis instance"""
    return RedisConnection.redis
