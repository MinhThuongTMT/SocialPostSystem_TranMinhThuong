from fastapi import APIRouter, HTTPException, status, Header, Query
from typing import Optional
from app.models.schemas import CommentCreate, CommentResponse, PaginatedResponse
from app.services.comment_service import CommentService
from app.services.audit_log_service import AuditLogService, ACTION_TYPES, RESOURCE_TYPES
from app.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

comment_service = CommentService()
audit_service = AuditLogService()


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(post_id: str, comment_data: CommentCreate, authorization: Optional[str] = Header(None)):
    """Add a comment to a post (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        comment = await comment_service.create_comment(post_id, user_id, comment_data.content)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["COMMENT_CREATED"],
            resource_type=RESOURCE_TYPES["COMMENT"],
            resource_id=str(comment["_id"]),
            details={"post_id": post_id}
        )
        
        return {
            "_id": str(comment["_id"]),
            "post_id": str(comment["post_id"]),
            "author_id": str(comment["author_id"]),
            "author": comment.get("author"),
            "content": comment["content"],
            "created_at": comment["created_at"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=PaginatedResponse)
async def get_post_comments(post_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get all comments for a post"""
    skip = (page - 1) * page_size
    comments = await comment_service.get_post_comments(post_id, skip=skip, limit=page_size)
    total = await comment_service.get_post_comments_count(post_id)
    
    comments_data = [
        {
            "_id": str(c["_id"]),
            "post_id": str(c["post_id"]),
            "author_id": str(c["author_id"]),
            "author": c.get("author"),
            "content": c["content"],
            "created_at": c["created_at"]
        }
        for c in comments
    ]
    
    return {
        "data": comments_data,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.delete("/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, authorization: Optional[str] = Header(None)):
    """Delete a comment (requires authentication and ownership)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        await comment_service.delete_comment(comment_id, user_id)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["COMMENT_DELETED"],
            resource_type=RESOURCE_TYPES["COMMENT"],
            resource_id=comment_id,
            details={"post_id": post_id}
        )
        
        return {"message": "Comment deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
