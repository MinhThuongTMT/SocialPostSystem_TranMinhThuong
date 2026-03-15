from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config.settings import settings

class MongoDBConnection:
    """MongoDB connection handler using Motor (async driver)"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional = None

async def connect_to_mongo():
    """Initialize MongoDB connection"""
    MongoDBConnection.client = AsyncIOMotorClient(settings.MONGODB_URL)
    MongoDBConnection.db = MongoDBConnection.client[settings.DATABASE_NAME]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if MongoDBConnection.client:
        MongoDBConnection.client.close()
        print("✅ Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return MongoDBConnection.db
