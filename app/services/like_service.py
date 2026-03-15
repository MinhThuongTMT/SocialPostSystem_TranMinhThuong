from typing import Optional
from bson import ObjectId
from app.config.database import get_database
from app.models.models import Like


class LikeService:
    """Service for handling like operations"""

    @staticmethod
    async def get_db():
        return get_database()

    async def like_post(self, post_id: str, user_id: str) -> dict:
        """Like a post"""
        db = await self.get_db()
        
        try:
            # Verify post exists
            post = await db["posts"].find_one({"_id": ObjectId(post_id)})
            if not post:
                raise ValueError("Post not found")
            
            # Check if already liked
            existing_like = await db["likes"].find_one({
                "post_id": ObjectId(post_id),
                "user_id": ObjectId(user_id)
            })
            
            if existing_like:
                raise ValueError("Already liked")
            
            like = Like(
                post_id=ObjectId(post_id),
                user_id=ObjectId(user_id)
            )
            
            result = await db["likes"].insert_one(like.to_dict())
            like_doc = await db["likes"].find_one({"_id": result.inserted_id})
            
            # Publish like.created event
            try:
                from app.services.event_consumer import event_consumer
                await event_consumer.publish_event("like.created", {
                    "post_id": post_id,
                    "user_id": user_id
                })
            except Exception as e:
                print(f"Event publish error: {str(e)}")
            
            return like_doc
        except Exception as e:
            raise ValueError(f"Error liking post: {str(e)}")

    async def unlike_post(self, post_id: str, user_id: str) -> bool:
        """Unlike a post"""
        db = await self.get_db()
        try:
            result = await db["likes"].delete_one({
                "post_id": ObjectId(post_id),
                "user_id": ObjectId(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Error unliking post: {str(e)}")

    async def is_post_liked_by_user(self, post_id: str, user_id: str) -> bool:
        """Check if user has liked a post"""
        db = await self.get_db()
        try:
            like = await db["likes"].find_one({
                "post_id": ObjectId(post_id),
                "user_id": ObjectId(user_id)
            })
            return like is not None
        except:
            return False

    async def get_post_likes_count(self, post_id: str) -> int:
        """Get total likes on a post"""
        db = await self.get_db()
        try:
            return await db["likes"].count_documents({"post_id": ObjectId(post_id)})
        except:
            return 0

    async def get_user_likes(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        """Get posts liked by a user"""
        db = await self.get_db()
        try:
            likes = await db["likes"].find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            
            # Get post details
            posts = []
            for like in likes:
                post = await db["posts"].find_one({"_id": like["post_id"]})
                if post:
                    posts.append(post)
            
            return posts
        except:
            return []
