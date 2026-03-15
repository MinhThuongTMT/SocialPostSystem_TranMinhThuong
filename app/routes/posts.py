from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import Optional
from app.models.schemas import PostCreate, PostUpdate, PostResponse, PaginatedResponse
from app.services.post_service import PostService
from app.services.audit_log_service import AuditLogService, ACTION_TYPES, RESOURCE_TYPES
from app.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/posts", tags=["posts"])

post_service = PostService()
audit_service = AuditLogService()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, authorization: Optional[str] = Header(None)):
    """Create a new post (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        post = await post_service.create_post(user_id, post_data.content)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["POST_CREATED"],
            resource_type=RESOURCE_TYPES["POST"],
            resource_id=str(post["_id"])
        )
        
        return {
            "_id": str(post["_id"]),
            "author_id": str(post["author_id"]),
            "content": post["content"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
            "likes_count": 0,
            "comments_count": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """Get post by ID"""
    post = await post_service.get_post_by_id(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "_id": str(post["_id"]),
        "author_id": str(post["author_id"]),
        "author": post.get("author"),
        "content": post["content"],
        "created_at": post["created_at"],
        "updated_at": post["updated_at"],
        "likes_count": post.get("likes_count", 0),
        "comments_count": post.get("comments_count", 0)
    }


@router.get("", response_model=PaginatedResponse)
async def get_all_posts(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get all posts with pagination"""
    skip = (page - 1) * page_size
    posts = await post_service.get_all_posts(skip=skip, limit=page_size)
    total = await post_service.get_total_posts_count()
    
    posts_data = [
        {
            "_id": str(p["_id"]),
            "author_id": str(p["author_id"]),
            "author": p.get("author"),
            "content": p["content"],
            "created_at": p["created_at"],
            "updated_at": p["updated_at"],
            "likes_count": p.get("likes_count", 0),
            "comments_count": p.get("comments_count", 0)
        }
        for p in posts
    ]
    
    return {
        "data": posts_data,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post_data: PostUpdate, authorization: Optional[str] = Header(None)):
    """Update post (requires authentication and ownership)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        post = await post_service.update_post(post_id, user_id, post_data.content)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["POST_UPDATED"],
            resource_type=RESOURCE_TYPES["POST"],
            resource_id=post_id
        )
        
        return {
            "_id": str(post["_id"]),
            "author_id": str(post["author_id"]),
            "content": post["content"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{post_id}")
async def delete_post(post_id: str, authorization: Optional[str] = Header(None)):
    """Delete post (requires authentication and ownership)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        await post_service.delete_post(post_id, user_id)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["POST_DELETED"],
            resource_type=RESOURCE_TYPES["POST"],
            resource_id=post_id
        )
        
        return {"message": "Post deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}", response_model=PaginatedResponse)
async def get_user_posts(user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get all posts by a specific user"""
    skip = (page - 1) * page_size
    posts = await post_service.get_user_posts(user_id, skip=skip, limit=page_size)
    total = await post_service.get_user_posts_count(user_id)
    
    posts_data = [
        {
            "_id": str(p["_id"]),
            "author_id": str(p["author_id"]),
            "content": p["content"],
            "created_at": p["created_at"],
            "updated_at": p["updated_at"],
            "likes_count": p.get("likes_count", 0),
            "comments_count": p.get("comments_count", 0)
        }
        for p in posts
    ]
    
    return {
        "data": posts_data,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }
