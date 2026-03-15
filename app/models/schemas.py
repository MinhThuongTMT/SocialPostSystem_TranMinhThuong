from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, *args, **kwargs):
        return {"type": "string", "pattern": "^[a-f0-9]{24}$"}


# ============ USER SCHEMAS ============
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    followers_count: int = 0
    following_count: int = 0
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ POST SCHEMAS ============
class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)

class PostResponse(PostBase):
    id: str = Field(alias="_id")
    author_id: str
    author: Optional[dict] = None
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ COMMENT SCHEMAS ============
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: str = Field(alias="_id")
    post_id: str
    author_id: str
    author: Optional[dict] = None
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ LIKE SCHEMAS ============
class LikeResponse(BaseModel):
    id: str = Field(alias="_id")
    post_id: str
    user_id: str
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ FOLLOW SCHEMAS ============
class FollowResponse(BaseModel):
    id: str = Field(alias="_id")
    follower_id: str
    following_id: str
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ AUDIT LOG SCHEMAS ============
class AuditLogCreate(BaseModel):
    user_id: str
    action: str  # CREATE_POST, LIKE_POST, FOLLOW_USER, etc.
    resource_type: str  # POST, COMMENT, USER, etc.
    resource_id: str
    details: Optional[dict] = None

class AuditLogResponse(AuditLogCreate):
    id: str = Field(alias="_id")
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}


# ============ PAGINATION SCHEMAS ============
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    data: List
    page: int
    page_size: int
    total: int
    total_pages: int
