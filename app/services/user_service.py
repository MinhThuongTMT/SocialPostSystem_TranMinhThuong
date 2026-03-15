import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from bson import ObjectId
from app.config.settings import settings
from app.config.database import get_database
from app.models.models import User
from app.models.schemas import UserCreate, UserResponse


class UserService:
    """Service for handling user operations"""

    @staticmethod
    async def get_db():
        return get_database()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    @staticmethod
    def create_access_token(user_id: str) -> str:
        """Create JWT token for user"""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[str]:
        """Decode JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def create_user(self, user_data: UserCreate) -> dict:
        """Create a new user"""
        db = await self.get_db()
        
        # Check if user already exists
        existing_user = await db["users"].find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=self.hash_password(user_data.password)
        )
        
        result = await db["users"].insert_one(user.to_dict())
        user_doc = await db["users"].find_one({"_id": result.inserted_id})
        return user_doc

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        db = await self.get_db()
        try:
            user = await db["users"].find_one({"_id": ObjectId(user_id)})
            return user
        except:
            return None

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        db = await self.get_db()
        return await db["users"].find_one({"username": username})

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        db = await self.get_db()
        return await db["users"].find_one({"email": email})

    async def update_user(self, user_id: str, update_data: dict) -> Optional[dict]:
        """Update user information"""
        db = await self.get_db()
        try:
            result = await db["users"].find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
            )
            return result
        except:
            return None

    async def get_all_users(self, skip: int = 0, limit: int = 10) -> list:
        """Get all users with pagination"""
        db = await self.get_db()
        users = await db["users"].find().skip(skip).limit(limit).to_list(length=None)
        return users

    async def get_total_users_count(self) -> int:
        """Get total number of users"""
        db = await self.get_db()
        return await db["users"].count_documents({})
