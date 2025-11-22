# ===================================
# api/notifications.py - Notification System
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.common import APIResponse
from backend.services.notification_service import notification_service
from backend.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def get_user_notifications(current_user_id: str = Depends(get_current_user)):
    """Get user notifications"""
    
    result = await notification_service.get_user_notifications(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Notifications retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )

@router.put("/{notification_id}/read", response_model=APIResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Mark notification as read"""
    
    result = await notification_service.mark_as_read(notification_id, current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Notification marked as read"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )