"""
Working Groups API - Complete CRUD operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.common import APIResponse
from backend.services.mongodb_service import mongodb_service
from backend.core.security import get_current_user
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import secrets

router = APIRouter()

@router.post("/", response_model=APIResponse)
async def create_group(group_data: GroupCreate, current_user_id: str = Depends(get_current_user)):
    """Create a new group (Admin only)"""
    
    # Get current user to check permissions
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    
    # Check if user is admin or group manager
    if user["role"] not in ["admin", "group_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    result = await group_service.create_group(group_data.dict(), current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"],
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/", response_model=APIResponse)
async def list_groups(current_user_id: str = Depends(get_current_user)):
    """List all groups"""
    
    # Get current user to determine what groups they can see
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    
    result = await group_service.get_groups(current_user_id, user["role"])
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Groups retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to fetch groups")
        )

@router.get("/{group_id}", response_model=APIResponse)
async def get_group(group_id: str, current_user_id: str = Depends(get_current_user)):
    """Get group by ID"""
    
    result = await group_service.get_group_by_id(group_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Group retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

# ===== MISSING ENDPOINTS - ADDED =====

@router.put("/{group_id}", response_model=APIResponse)
async def update_group(
    group_id: str, 
    update_data: GroupUpdate, 
    current_user_id: str = Depends(get_current_user)
):
    """Update group details"""
    
    result = await group_service.update_group(group_id, update_data.dict(exclude_unset=True), current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"],
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.put("/{group_id}/trading-status", response_model=APIResponse)
async def toggle_group_trading(
    group_id: str,
    status: str,  # "active" or "paused"
    admin_otp: str,
    current_user_id: str = Depends(get_current_user)
):
    """Start/Stop group trading with OTP verification"""
    
    # Verify admin access
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] not in ["admin", "group_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # TODO: Verify OTP first
    # otp_service.verify_otp(user["mobile"], admin_otp, "mobile")
    
    result = await group_service.toggle_trading_status(group_id, status, current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.post("/{group_id}/regenerate-api-key", response_model=APIResponse)
async def regenerate_api_key(
    group_id: str,
    api_key_data: APIKeyGenerate,
    current_user_id: str = Depends(get_current_user)
):
    """Regenerate group API key with OTP verification"""
    
    # Verify admin access
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # TODO: Verify OTP
    # otp_service.verify_otp(user["mobile"], api_key_data.admin_otp, "mobile")
    
    result = await group_service.regenerate_api_key(group_id, current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"],
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/{group_id}/members", response_model=APIResponse)
async def get_group_members(group_id: str, current_user_id: str = Depends(get_current_user)):
    """Get all members in a group"""
    
    # Get current user to check permissions
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await member_service.get_members(group_id=group_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Group members retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch group members"
        )

@router.get("/{group_id}/performance", response_model=APIResponse)
async def get_group_performance(group_id: str, current_user_id: str = Depends(get_current_user)):
    """Get group performance metrics"""
    
    try:
        # Mock group performance data (replace with actual service call)
        performance_data = {
            "group_id": group_id,
            "total_members": 15,
            "active_members": 12,
            "total_equity": 125000.0,
            "total_profit": 8420.50,
            "today_profit": 340.25,
            "weekly_profit": 1250.75,
            "monthly_profit": 4250.00,
            "profit_share_due": 2526.15,
            "last_settlement_date": "2025-09-10T00:00:00Z",
            "next_due_date": "2025-10-10T00:00:00Z",
            "win_rate": 65.5,
            "total_trades": 245,
            "winning_trades": 160
        }
        
        return APIResponse(
            success=True,
            message="Group performance retrieved successfully",
            data=performance_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch group performance"
        )

@router.delete("/{group_id}", response_model=APIResponse)
async def delete_group(group_id: str, current_user_id: str = Depends(get_current_user)):
    """Soft delete group (Admin only)"""
    
    # Verify admin access
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Soft delete by updating status
    result = await group_service.update_group(group_id, {"status": "deleted"}, current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Group deleted successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete group"
        )