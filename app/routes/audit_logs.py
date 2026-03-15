from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional
from app.models.schemas import AuditLogResponse, PaginatedResponse
from app.services.audit_log_service import AuditLogService
from app.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

audit_service = AuditLogService()


@router.get("/user/{user_id}", response_model=PaginatedResponse)
async def get_user_audit_logs(user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50)):
    """Get audit logs for a specific user (admin only)"""
    skip = (page - 1) * page_size
    logs = await audit_service.get_user_audit_logs(user_id, skip=skip, limit=page_size)
    
    # Format logs for response
    logs_data = [
        {
            "_id": str(log["_id"]),
            "user_id": str(log["user_id"]),
            "action": log["action"],
            "resource_type": log["resource_type"],
            "resource_id": str(log["resource_id"]),
            "details": log.get("details"),
            "created_at": log["created_at"]
        }
        for log in logs
    ]
    
    return {
        "data": logs_data,
        "page": page,
        "page_size": page_size,
        "total": len(logs_data),
        "total_pages": 1
    }


@router.get("/resource/{resource_type}/{resource_id}", response_model=PaginatedResponse)
async def get_resource_audit_logs(resource_type: str, resource_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50)):
    """Get audit logs for a specific resource"""
    skip = (page - 1) * page_size
    logs = await audit_service.get_resource_audit_logs(resource_type, resource_id, skip=skip, limit=page_size)
    
    # Format logs for response
    logs_data = [
        {
            "_id": str(log["_id"]),
            "user_id": str(log["user_id"]),
            "action": log["action"],
            "resource_type": log["resource_type"],
            "resource_id": str(log["resource_id"]),
            "details": log.get("details"),
            "created_at": log["created_at"]
        }
        for log in logs
    ]
    
    return {
        "data": logs_data,
        "page": page,
        "page_size": page_size,
        "total": len(logs_data),
        "total_pages": 1
    }


@router.get("/action/{action}", response_model=PaginatedResponse)
async def get_action_audit_logs(action: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50)):
    """Get audit logs for a specific action type"""
    skip = (page - 1) * page_size
    logs = await audit_service.get_action_audit_logs(action, skip=skip, limit=page_size)
    
    # Format logs for response
    logs_data = [
        {
            "_id": str(log["_id"]),
            "user_id": str(log["user_id"]),
            "action": log["action"],
            "resource_type": log["resource_type"],
            "resource_id": str(log["resource_id"]),
            "details": log.get("details"),
            "created_at": log["created_at"]
        }
        for log in logs
    ]
    
    return {
        "data": logs_data,
        "page": page,
        "page_size": page_size,
        "total": len(logs_data),
        "total_pages": 1
    }
