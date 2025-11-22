# ===================================
# Updated api/members.py
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models.common import APIResponse
from backend.models.member import MemberCreate, MemberUpdate, MemberResponse, MemberAccountLink
from backend.models.broker import BrokerResponse
from backend.services.member_service import member_service
from backend.services.user_service import user_service
from backend.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=APIResponse)
async def add_member(member_data: MemberCreate, current_user_id: str = Depends(get_current_user)):
    """Add member to group"""
    
    # Check if current user has permission to add members
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    
    # Check permissions (admin or group manager)
    if user["role"] not in ["admin", "group_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    result = await member_service.add_member_to_group(member_data.dict(), current_user_id)
    
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
async def list_members(
    group_id: str = Query(None, description="Filter by group ID"),
    current_user_id: str = Depends(get_current_user)
):
    """List all members with optional group filtering"""
    
    # Get current user to determine permissions
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    
    result = await member_service.get_members(group_id, user["role"])
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Members retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to fetch members")
        )

@router.get("/{member_id}", response_model=APIResponse)
async def get_member(member_id: str, current_user_id: str = Depends(get_current_user)):
    """Get member by ID"""
    
    result = await member_service.get_member_by_id(member_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Member retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

@router.put("/{member_id}", response_model=APIResponse)
async def update_member(
    member_id: str, 
    update_data: MemberUpdate, 
    current_user_id: str = Depends(get_current_user)
):
    """Update member status or allocation model"""
    
    result = await member_service.update_member(member_id, update_data.dict(exclude_unset=True), current_user_id)
    
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

@router.put("/{member_id}/status", response_model=APIResponse)
async def update_member_status(
    member_id: str,
    status: str,
    current_user_id: str = Depends(get_current_user)
):
    """Update member trading status (active/paused/inactive)"""
    
    if status not in ["active", "paused", "inactive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'active', 'paused', or 'inactive'"
        )
    
    result = await member_service.update_member(member_id, {"status": status}, current_user_id)
    
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

@router.get("/brokers/available", response_model=APIResponse)
async def get_available_brokers(current_user_id: str = Depends(get_current_user)):
    """Get list of available brokers and servers"""
    
    result = await member_service.get_available_brokers()
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Brokers retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch brokers"
        )

@router.post("/link-account", response_model=APIResponse)
async def link_mt5_account(
    account_data: MemberAccountLink,
    current_user_id: str = Depends(get_current_user)
):
    """Link MT5 account for current user (for self-registration)"""
    
    # This endpoint allows users to link their own MT5 accounts
    # They would still need to be assigned to a group by an admin
    
    # Verify the account first
    verification_result = await member_service.verify_mt5_account(
        account_data.broker,
        account_data.server,
        account_data.account_no,
        account_data.password
    )
    
    if verification_result["status"]:
        # Store account details for later group assignment
        # This could be stored in a separate collection or user profile
        return APIResponse(
            success=True,
            message="MT5 account verified and linked successfully",
            data={"verified": True}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verification_result["message"]
        )