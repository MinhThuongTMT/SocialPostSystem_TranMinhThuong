from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class User:
    """User MongoDB Model"""
    
    def __init__(self, username: str, email: str, password_hash: str):
        self._id = ObjectId()
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.bio = None
        self.avatar_url = None
        self.created_at = datetime.utcnow()
        self.followers_count = 0
        self.following_count = 0

    def to_dict(self):
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at,
            "followers_count": self.followers_count,
            "following_count": self.following_count
        }


class Post:
    """Post MongoDB Model"""
    
    def __init__(self, author_id: ObjectId, content: str):
        self._id = ObjectId()
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Comment:
    """Comment MongoDB Model"""
    
    def __init__(self, post_id: ObjectId, author_id: ObjectId, content: str):
        self._id = ObjectId()
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at
        }


class Like:
    """Like MongoDB Model"""
    
    def __init__(self, post_id: ObjectId, user_id: ObjectId):
        self._id = ObjectId()
        self.post_id = post_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "created_at": self.created_at
        }


class Follow:
    """Follow MongoDB Model"""
    
    def __init__(self, follower_id: ObjectId, following_id: ObjectId):
        self._id = ObjectId()
        self.follower_id = follower_id
        self.following_id = following_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "follower_id": self.follower_id,
            "following_id": self.following_id,
            "created_at": self.created_at
        }


class AuditLog:
    """Audit Log MongoDB Model - for tracking actions"""
    
    def __init__(self, user_id: ObjectId, action: str, resource_type: str, resource_id: ObjectId, details: Optional[dict] = None):
        self._id = ObjectId()
        self.user_id = user_id
        self.action = action  # CREATE_POST, LIKE_POST, FOLLOW_USER, etc.
        self.resource_type = resource_type  # POST, COMMENT, USER, etc.
        self.resource_id = resource_id
        self.details = details or {}
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "created_at": self.created_at
        }
