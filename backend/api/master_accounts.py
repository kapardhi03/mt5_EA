# ===================================
# api/master_accounts.py - Master Account Management
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from backend.models.common import APIResponse
from backend.services.master_account_service import master_account_service
from backend.services.user_service import user_service
from backend.core.security import get_current_user
from typing import Literal, Optional

router = APIRouter()

class MasterAccountCreate(BaseModel):
    broker: str = Field(..., min_length=1)
    server: str = Field(..., min_length=1)
    account_no: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    investor_password: Optional[str] = None
    account_type: Literal["netting", "hedging"] = "netting"

async def verify_admin(current_user_id: str = Depends(get_current_user)):
    """Verify admin access"""
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return user

@router.post("/", response_model=APIResponse)
async def create_master_account(
    account_data: MasterAccountCreate,
    admin_user = Depends(verify_admin)
):
    """Create master account (Admin only)"""
    
    result = await master_account_service.create_master_account(
        account_data.dict(), 
        admin_user["user_id"]
    )
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"],
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create master account"
        )

@router.get("/", response_model=APIResponse)
async def list_master_accounts(admin_user = Depends(verify_admin)):
    """List all master accounts (Admin only)"""
    
    result = await master_account_service.get_master_accounts()
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Master accounts retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch master accounts"
        )

@router.get("/health", response_model=APIResponse)
async def get_master_accounts_health(admin_user = Depends(verify_admin)):
    """Get master account health status (Admin only)"""
    
    result = await master_account_service.get_master_account_health()
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Master account health retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch master account health"
        )