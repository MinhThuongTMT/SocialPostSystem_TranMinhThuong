"""
Rate Limiting Middleware using Redis
Implements token bucket algorithm for API rate limiting
"""
from typing import Optional, Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as aioredis
import time
from ..config.redis_config import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that limits requests per client IP
    
    Default: 100 requests per hour per IP
    Can be customized per endpoint
    """
    
    def __init__(self, app, requests_per_hour: int = 100):
        super().__init__(app)
        self.requests_per_hour = requests_per_hour
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Exclude health check from rate limiting
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Create rate limit key
        rate_limit_key = f"rate_limit:{client_ip}"
        
        try:
            redis = await get_redis()
            
            # Get current request count
            current = await redis.get(rate_limit_key)
            
            if current is None:
                # First request, set count to 1 with TTL of 1 hour
                await redis.setex(rate_limit_key, 3600, 1)
                request.state.remaining_requests = self.requests_per_hour - 1
            else:
                current_count = int(current)
                
                # Check if limit exceeded
                if current_count >= self.requests_per_hour:
                    # Get TTL remaining
                    ttl = await redis.ttl(rate_limit_key)
                    
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Rate limit exceeded",
                            "retry_after": ttl,
                            "limit": self.requests_per_hour,
                            "window": "1 hour"
                        },
                        headers={
                            "Retry-After": str(ttl),
                            "X-RateLimit-Limit": str(self.requests_per_hour),
                            "X-RateLimit-Remaining": "0"
                        }
                    )
                
                # Increment counter
                await redis.incr(rate_limit_key)
                remaining = self.requests_per_hour - current_count - 1
                request.state.remaining_requests = remaining
            
            # Add rate limit info to response headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining"] = str(request.state.remaining_requests)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 3600)
            
            return response
            
        except Exception as e:
            # If Redis fails, allow request but log error
            print(f"Rate limit error: {str(e)}")
            return await call_next(request)


class PerUserRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting per authenticated user
    More strict for authenticated endpoints
    
    Default: 500 requests per hour per user
    """
    
    def __init__(self, app, requests_per_hour: int = 500):
        super().__init__(app)
        self.requests_per_hour = requests_per_hour
        self.redis_conn = RedisConnection()
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Only apply to authenticated endpoints
        if not hasattr(request.state, "user_id"):
            return await call_next(request)
        
        user_id = request.state.user_id
        rate_limit_key = f"user_rate_limit:{user_id}"
        
        try:
            redis = await self.redis_conn.get_redis()
            
            current = await redis.get(rate_limit_key)
            
            if current is None:
                await redis.setex(rate_limit_key, 3600, 1)
            else:
                current_count = int(current)
                
                if current_count >= self.requests_per_hour:
                    ttl = await redis.ttl(rate_limit_key)
                    
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": f"User rate limit exceeded. {self.requests_per_hour} requests per hour",
                            "retry_after": ttl
                        },
                        headers={"Retry-After": str(ttl)}
                    )
                
                await redis.incr(rate_limit_key)
            
            return await call_next(request)
            
        except Exception as e:
            print(f"User rate limit error: {str(e)}")
            return await call_next(request)
