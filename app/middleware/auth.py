from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.user_service import UserService


class AuthMiddleware:
    """Middleware for token-based authentication"""

    @staticmethod
    async def get_current_user(token: str):
        """Verify token and return user_id"""
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token"
            )
        
        user_service = UserService()
        user_id = user_service.decode_token(token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Verify user exists
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user_id
