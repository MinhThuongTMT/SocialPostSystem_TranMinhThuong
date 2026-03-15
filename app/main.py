from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import connect_to_mongo, close_mongo_connection
from app.config.redis_config import connect_to_redis, close_redis_connection
from app.routes import health, users, posts, comments, likes, follows, audit_logs
from app.config.settings import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.background_jobs import background_jobs_service
from app.services.event_consumer import event_consumer

# Security scheme
security = HTTPBearer(description="JWT Token")

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting application...")
    await connect_to_mongo()
    await connect_to_redis()
    
    # Initialize and start background jobs
    background_jobs_service.initialize()
    background_jobs_service.start()
    
    # Start event consumer
    await event_consumer.start()
    
    print("✅ All connections established")
    print("✅ Background jobs started")
    print("✅ Event consumer started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    await event_consumer.stop()
    background_jobs_service.stop()
    await close_mongo_connection()
    await close_redis_connection()
    print("✅ All connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "users",
            "description": "User management and authentication"
        },
        {
            "name": "posts",
            "description": "Post management"
        },
        {
            "name": "comments",
            "description": "Comment management"
        },
        {
            "name": "likes",
            "description": "Like management"
        },
        {
            "name": "follows",
            "description": "Follow management"
        },
        {
            "name": "audit_logs",
            "description": "Audit logs"
        }
    ]
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Modify OpenAPI schema to include security properly
original_openapi = app.openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = original_openapi()
    
    if openapi_schema:
        openapi_schema["components"]["securitySchemes"] = {
            "HTTPBearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token"
            }
        }
        openapi_schema["security"] = [{"HTTPBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Include routers
app.include_router(health.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(follows.router)
app.include_router(audit_logs.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
