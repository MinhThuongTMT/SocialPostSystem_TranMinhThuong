from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.config.database import get_database
from app.models.models import Post


class PostService:
    """Service for handling post operations"""

    @staticmethod
    async def get_db():
        return get_database()

    async def create_post(self, author_id: str, content: str) -> dict:
        """Create a new post"""
        db = await self.get_db()
        
        try:
            post = Post(
                author_id=ObjectId(author_id),
                content=content
            )
            
            result = await db["posts"].insert_one(post.to_dict())
            post_doc = await db["posts"].find_one({"_id": result.inserted_id})
            
            # Publish post.created event
            try:
                from app.services.event_consumer import event_consumer
                await event_consumer.publish_event("post.created", {
                    "post_id": str(post_doc["_id"]),
                    "user_id": str(author_id),
                    "content": content[:50]
                })
            except Exception as e:
                print(f"Event publish error: {str(e)}")
            
            return post_doc
        except Exception as e:
            raise ValueError(f"Error creating post: {str(e)}")

    async def get_post_by_id(self, post_id: str) -> Optional[dict]:
        """Get post by ID"""
        db = await self.get_db()
        try:
            post = await db["posts"].find_one({"_id": ObjectId(post_id)})
            if post:
                # Add author info
                author = await db["users"].find_one({"_id": post["author_id"]})
                post["author"] = {
                    "_id": str(author["_id"]),
                    "username": author["username"]
                } if author else None
            return post
        except:
            return None

    async def get_all_posts(self, skip: int = 0, limit: int = 10) -> list:
        """Get all posts with pagination (newest first)"""
        db = await self.get_db()
        posts = await db["posts"].find().sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Add author info and counts
        for post in posts:
            author = await db["users"].find_one({"_id": post["author_id"]})
            post["author"] = {
                "_id": str(author["_id"]),
                "username": author["username"]
            } if author else None
            
            likes_count = await db["likes"].count_documents({"post_id": post["_id"]})
            comments_count = await db["comments"].count_documents({"post_id": post["_id"]})
            
            post["likes_count"] = likes_count
            post["comments_count"] = comments_count
        
        return posts

    async def get_user_posts(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        """Get posts by specific user"""
        db = await self.get_db()
        try:
            posts = await db["posts"].find({"author_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            
            # Add counts
            for post in posts:
                likes_count = await db["likes"].count_documents({"post_id": post["_id"]})
                comments_count = await db["comments"].count_documents({"post_id": post["_id"]})
                
                post["likes_count"] = likes_count
                post["comments_count"] = comments_count
            
            return posts
        except:
            return []

    async def update_post(self, post_id: str, author_id: str, content: str) -> Optional[dict]:
        """Update post content"""
        db = await self.get_db()
        try:
            # Verify ownership
            post = await db["posts"].find_one({"_id": ObjectId(post_id)})
            if not post or str(post["author_id"]) != author_id:
                raise ValueError("Unauthorized")
            
            result = await db["posts"].find_one_and_update(
                {"_id": ObjectId(post_id)},
                {
                    "$set": {
                        "content": content,
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except Exception as e:
            raise ValueError(f"Error updating post: {str(e)}")

    async def delete_post(self, post_id: str, author_id: str) -> bool:
        """Delete post (only by author)"""
        db = await self.get_db()
        try:
            # Verify ownership
            post = await db["posts"].find_one({"_id": ObjectId(post_id)})
            if not post or str(post["author_id"]) != author_id:
                raise ValueError("Unauthorized")
            
            # Delete post
            await db["posts"].delete_one({"_id": ObjectId(post_id)})
            
            # Delete related comments, likes
            await db["comments"].delete_many({"post_id": ObjectId(post_id)})
            await db["likes"].delete_many({"post_id": ObjectId(post_id)})
            
            # Publish post.deleted event
            try:
                from app.services.event_consumer import event_consumer
                await event_consumer.publish_event("post.deleted", {
                    "post_id": post_id,
                    "user_id": author_id
                })
            except Exception as e:
                print(f"Event publish error: {str(e)}")
            
            return True
        except Exception as e:
            raise ValueError(f"Error deleting post: {str(e)}")

    async def get_total_posts_count(self) -> int:
        """Get total number of posts"""
        db = await self.get_db()
        return await db["posts"].count_documents({})

    async def get_user_posts_count(self, user_id: str) -> int:
        """Get total posts by user"""
        db = await self.get_db()
        try:
            return await db["posts"].count_documents({"author_id": ObjectId(user_id)})
        except:
            return 0
