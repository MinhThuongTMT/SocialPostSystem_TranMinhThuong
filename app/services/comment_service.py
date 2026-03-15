from typing import Optional, List
from bson import ObjectId
from app.config.database import get_database
from app.models.models import Comment


class CommentService:
    """Service for handling comment operations"""

    @staticmethod
    async def get_db():
        return get_database()

    async def create_comment(self, post_id: str, author_id: str, content: str) -> dict:
        """Create a new comment on a post"""
        db = await self.get_db()
        
        try:
            # Verify post exists
            post = await db["posts"].find_one({"_id": ObjectId(post_id)})
            if not post:
                raise ValueError("Post not found")
            
            comment = Comment(
                post_id=ObjectId(post_id),
                author_id=ObjectId(author_id),
                content=content
            )
            
            result = await db["comments"].insert_one(comment.to_dict())
            comment_doc = await db["comments"].find_one({"_id": result.inserted_id})
            
            # Add author info
            author = await db["users"].find_one({"_id": ObjectId(author_id)})
            comment_doc["author"] = {
                "_id": str(author["_id"]),
                "username": author["username"]
            } if author else None
            
            return comment_doc
        except Exception as e:
            raise ValueError(f"Error creating comment: {str(e)}")

    async def get_post_comments(self, post_id: str, skip: int = 0, limit: int = 10) -> list:
        """Get all comments for a post"""
        db = await self.get_db()
        try:
            comments = await db["comments"].find({"post_id": ObjectId(post_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            
            # Add author info
            for comment in comments:
                author = await db["users"].find_one({"_id": comment["author_id"]})
                comment["author"] = {
                    "_id": str(author["_id"]),
                    "username": author["username"]
                } if author else None
            
            return comments
        except:
            return []

    async def delete_comment(self, comment_id: str, author_id: str) -> bool:
        """Delete comment (only by author)"""
        db = await self.get_db()
        try:
            # Verify ownership
            comment = await db["comments"].find_one({"_id": ObjectId(comment_id)})
            if not comment or str(comment["author_id"]) != author_id:
                raise ValueError("Unauthorized")
            
            await db["comments"].delete_one({"_id": ObjectId(comment_id)})
            return True
        except Exception as e:
            raise ValueError(f"Error deleting comment: {str(e)}")

    async def get_post_comments_count(self, post_id: str) -> int:
        """Get total comments on a post"""
        db = await self.get_db()
        try:
            return await db["comments"].count_documents({"post_id": ObjectId(post_id)})
        except:
            return 0
