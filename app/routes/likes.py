from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from app.services.like_service import LikeService
from app.services.audit_log_service import AuditLogService, ACTION_TYPES, RESOURCE_TYPES
from app.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/posts/{post_id}", tags=["likes"])

like_service = LikeService()
audit_service = AuditLogService()


@router.post("/like")
async def like_post(post_id: str, authorization: Optional[str] = Header(None)):
    """Like a post (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        like = await like_service.like_post(post_id, user_id)
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["POST_LIKED"],
            resource_type=RESOURCE_TYPES["LIKE"],
            resource_id=str(like["_id"]),
            details={"post_id": post_id}
        )
        
        return {"message": "Post liked successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/like")
async def unlike_post(post_id: str, authorization: Optional[str] = Header(None)):
    """Unlike a post (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = await AuthMiddleware.get_current_user(token)
    
    try:
        result = await like_service.unlike_post(post_id, user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Like not found")
        
        # Log action
        await audit_service.log_action(
            user_id=user_id,
            action=ACTION_TYPES["POST_UNLIKED"],
            resource_type=RESOURCE_TYPES["LIKE"],
            resource_id=post_id,
            details={"post_id": post_id}
        )
        
        return {"message": "Post unliked successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/likes")
async def get_post_likes(post_id: str):
    """Get likes count for a post"""
    try:
        count = await like_service.get_post_likes_count(post_id)
        return {"post_id": post_id, "likes_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
