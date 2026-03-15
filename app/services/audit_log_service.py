from typing import Optional
from bson import ObjectId
from datetime import datetime
from app.config.database import get_database
from app.models.models import AuditLog


class AuditLogService:
    """Service for audit log operations"""

    @staticmethod
    async def get_db():
        return get_database()

    async def log_action(self, user_id: str, action: str, resource_type: str, resource_id: str, details: Optional[dict] = None) -> dict:
        """Log user action for audit trail"""
        db = await self.get_db()
        
        try:
            audit_log = AuditLog(
                user_id=ObjectId(user_id),
                action=action,
                resource_type=resource_type,
                resource_id=ObjectId(resource_id),
                details=details or {}
            )
            
            result = await db["audit_logs"].insert_one(audit_log.to_dict())
            log_doc = await db["audit_logs"].find_one({"_id": result.inserted_id})
            return log_doc
        except Exception as e:
            print(f"Error logging action: {str(e)}")
            return {}

    async def get_user_audit_logs(self, user_id: str, skip: int = 0, limit: int = 50) -> list:
        """Get audit logs for a specific user"""
        db = await self.get_db()
        try:
            logs = await db["audit_logs"].find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            return logs
        except:
            return []

    async def get_resource_audit_logs(self, resource_type: str, resource_id: str, skip: int = 0, limit: int = 50) -> list:
        """Get audit logs for a specific resource"""
        db = await self.get_db()
        try:
            logs = await db["audit_logs"].find({
                "resource_type": resource_type,
                "resource_id": ObjectId(resource_id)
            }).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            return logs
        except:
            return []

    async def get_action_audit_logs(self, action: str, skip: int = 0, limit: int = 50) -> list:
        """Get audit logs for a specific action type"""
        db = await self.get_db()
        try:
            logs = await db["audit_logs"].find({"action": action}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            return logs
        except:
            return []


# Action types for logging
ACTION_TYPES = {
    "USER_CREATED": "USER_CREATED",
    "USER_UPDATED": "USER_UPDATED",
    "POST_CREATED": "POST_CREATED",
    "POST_UPDATED": "POST_UPDATED",
    "POST_DELETED": "POST_DELETED",
    "COMMENT_CREATED": "COMMENT_CREATED",
    "COMMENT_DELETED": "COMMENT_DELETED",
    "POST_LIKED": "POST_LIKED",
    "POST_UNLIKED": "POST_UNLIKED",
    "USER_FOLLOWED": "USER_FOLLOWED",
    "USER_UNFOLLOWED": "USER_UNFOLLOWED"
}


# Resource types for logging
RESOURCE_TYPES = {
    "USER": "USER",
    "POST": "POST",
    "COMMENT": "COMMENT",
    "LIKE": "LIKE",
    "FOLLOW": "FOLLOW"
}
