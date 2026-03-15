from fastapi import APIRouter, HTTPException, status, Header, Query
from typing import Optional
from app.models.schemas import PaginatedResponse
from app.services.follow_service import FollowService
from app.services.audit_log_service import AuditLogService, ACTION_TYPES, RESOURCE_TYPES
from app.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/users/{user_id}", tags=["follows"])

follow_service = FollowService()
audit_service = AuditLogService()


@router.post("/follow")
async def follow_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Follow a user (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    follower_id = await AuthMiddleware.get_current_user(token)
    
    try:
        follow = await follow_service.follow_user(follower_id, user_id)
        
        # Log action
        await audit_service.log_action(
            user_id=follower_id,
            action=ACTION_TYPES["USER_FOLLOWED"],
            resource_type=RESOURCE_TYPES["FOLLOW"],
            resource_id=str(follow["_id"]),
            details={"following_id": user_id}
        )
        
        return {"message": "User followed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/follow")
async def unfollow_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Unfollow a user (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    follower_id = await AuthMiddleware.get_current_user(token)
    
    try:
        result = await follow_service.unfollow_user(follower_id, user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Follow relationship not found")
        
        # Log action
        await audit_service.log_action(
            user_id=follower_id,
            action=ACTION_TYPES["USER_UNFOLLOWED"],
            resource_type=RESOURCE_TYPES["FOLLOW"],
            resource_id=user_id,
            details={"following_id": user_id}
        )
        
        return {"message": "User unfollowed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/followers", response_model=PaginatedResponse)
async def get_followers(user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get list of followers for a user"""
    skip = (page - 1) * page_size
    followers = await follow_service.get_followers(user_id, skip=skip, limit=page_size)
    total = await follow_service.get_followers_count(user_id)
    
    return {
        "data": followers,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/following", response_model=PaginatedResponse)
async def get_following(user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get list of users that this user is following"""
    skip = (page - 1) * page_size
    following = await follow_service.get_following(user_id, skip=skip, limit=page_size)
    total = await follow_service.get_following_count(user_id)
    
    return {
        "data": following,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/followers/count")
async def get_followers_count(user_id: str):
    """Get followers count for a user"""
    try:
        count = await follow_service.get_followers_count(user_id)
        return {"user_id": user_id, "followers_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/following/count")
async def get_following_count(user_id: str):
    """Get following count for a user"""
    try:
        count = await follow_service.get_following_count(user_id)
        return {"user_id": user_id, "following_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
