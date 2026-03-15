from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import Optional
import logging
from app.models.schemas import UserCreate, UserResponse, PaginationParams, PaginatedResponse
from app.services.user_service import UserService
from app.services.audit_log_service import AuditLogService, ACTION_TYPES, RESOURCE_TYPES
from app.middleware.auth import AuthMiddleware

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()
audit_service = AuditLogService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await user_service.create_user(user_data)
        
        # Log action
        await audit_service.log_action(
            user_id=str(user["_id"]),
            action=ACTION_TYPES["USER_CREATED"],
            resource_type=RESOURCE_TYPES["USER"],
            resource_id=str(user["_id"])
        )
        
        return {
            "_id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "bio": user.get("bio"),
            "avatar_url": user.get("avatar_url"),
            "created_at": user["created_at"],
            "followers_count": user.get("followers_count", 0),
            "following_count": user.get("following_count", 0)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"User registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login_user(username: str, password: str):
    """Login user and return access token"""
    user = await user_service.get_user_by_username(username)
    
    if not user or not user_service.verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = user_service.create_access_token(str(user["_id"]))
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "username": user["username"]
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID"""
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "bio": user.get("bio"),
        "avatar_url": user.get("avatar_url"),
        "created_at": user["created_at"],
        "followers_count": user.get("followers_count", 0),
        "following_count": user.get("following_count", 0)
    }


@router.get("", response_model=PaginatedResponse)
async def get_all_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get all users with pagination"""
    skip = (page - 1) * page_size
    users = await user_service.get_all_users(skip=skip, limit=page_size)
    total = await user_service.get_total_users_count()
    
    users_data = [
        {
            "_id": str(u["_id"]),
            "username": u["username"],
            "email": u["email"],
            "bio": u.get("bio"),
            "avatar_url": u.get("avatar_url"),
            "created_at": u["created_at"],
            "followers_count": u.get("followers_count", 0),
            "following_count": u.get("following_count", 0)
        }
        for u in users
    ]
    
    return {
        "data": users_data,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.put("/{user_id}")
async def update_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Update user profile (requires authentication)"""
    # Verify user is authenticated
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    current_user_id = await AuthMiddleware.get_current_user(token)
    
    # Can only update own profile
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    raise HTTPException(status_code=501, detail="Feature not yet implemented")
