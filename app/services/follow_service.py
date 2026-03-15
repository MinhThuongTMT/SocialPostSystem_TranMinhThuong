from typing import Optional, List
from bson import ObjectId
from app.config.database import get_database
from app.models.models import Follow


class FollowService:
    """Service for handling follow operations"""

    @staticmethod
    async def get_db():
        return get_database()

    async def follow_user(self, follower_id: str, following_id: str) -> dict:
        """Follow a user"""
        db = await self.get_db()
        
        try:
            # Can't follow yourself
            if follower_id == following_id:
                raise ValueError("Cannot follow yourself")
            
            # Verify both users exist
            follower = await db["users"].find_one({"_id": ObjectId(follower_id)})
            following = await db["users"].find_one({"_id": ObjectId(following_id)})
            
            if not follower or not following:
                raise ValueError("User not found")
            
            # Check if already following
            existing_follow = await db["follows"].find_one({
                "follower_id": ObjectId(follower_id),
                "following_id": ObjectId(following_id)
            })
            
            if existing_follow:
                raise ValueError("Already following")
            
            follow = Follow(
                follower_id=ObjectId(follower_id),
                following_id=ObjectId(following_id)
            )
            
            result = await db["follows"].insert_one(follow.to_dict())
            
            # Update user counts
            await db["users"].update_one(
                {"_id": ObjectId(follower_id)},
                {"$inc": {"following_count": 1}}
            )
            
            await db["users"].update_one(
                {"_id": ObjectId(following_id)},
                {"$inc": {"followers_count": 1}}
            )
            
            follow_doc = await db["follows"].find_one({"_id": result.inserted_id})
            return follow_doc
        except Exception as e:
            raise ValueError(f"Error following user: {str(e)}")

    async def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        db = await self.get_db()
        try:
            result = await db["follows"].delete_one({
                "follower_id": ObjectId(follower_id),
                "following_id": ObjectId(following_id)
            })
            
            if result.deleted_count > 0:
                # Update user counts
                await db["users"].update_one(
                    {"_id": ObjectId(follower_id)},
                    {"$inc": {"following_count": -1}}
                )
                
                await db["users"].update_one(
                    {"_id": ObjectId(following_id)},
                    {"$inc": {"followers_count": -1}}
                )
                return True
            return False
        except Exception as e:
            raise ValueError(f"Error unfollowing user: {str(e)}")

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        """Check if user is following another user"""
        db = await self.get_db()
        try:
            follow = await db["follows"].find_one({
                "follower_id": ObjectId(follower_id),
                "following_id": ObjectId(following_id)
            })
            return follow is not None
        except:
            return False

    async def get_followers(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        """Get list of followers"""
        db = await self.get_db()
        try:
            follows = await db["follows"].find({"following_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            
            # Get user details
            followers = []
            for follow in follows:
                user = await db["users"].find_one({"_id": follow["follower_id"]})
                if user:
                    followers.append({
                        "_id": str(user["_id"]),
                        "username": user["username"],
                        "bio": user.get("bio"),
                        "avatar_url": user.get("avatar_url")
                    })
            
            return followers
        except:
            return []

    async def get_following(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        """Get list of users that this user is following"""
        db = await self.get_db()
        try:
            follows = await db["follows"].find({"follower_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            
            # Get user details
            following = []
            for follow in follows:
                user = await db["users"].find_one({"_id": follow["following_id"]})
                if user:
                    following.append({
                        "_id": str(user["_id"]),
                        "username": user["username"],
                        "bio": user.get("bio"),
                        "avatar_url": user.get("avatar_url")
                    })
            
            return following
        except:
            return []

    async def get_followers_count(self, user_id: str) -> int:
        """Get total followers count"""
        db = await self.get_db()
        try:
            return await db["follows"].count_documents({"following_id": ObjectId(user_id)})
        except:
            return 0

    async def get_following_count(self, user_id: str) -> int:
        """Get total following count"""
        db = await self.get_db()
        try:
            return await db["follows"].count_documents({"follower_id": ObjectId(user_id)})
        except:
            return 0
