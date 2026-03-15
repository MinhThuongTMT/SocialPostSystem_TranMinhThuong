from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongo:27017"
    DATABASE_NAME: str = "social_post_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # API Configuration
    API_TITLE: str = "Social Post System API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "A comprehensive social media platform API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
