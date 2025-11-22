# ===================================
# api/users.py - User Dashboard & Profile Management
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.common import APIResponse
from backend.models.user_dashboard import UserDashboard, ProfileUpdate, PasswordChange
from backend.services.user_service import user_service
from backend.services.user_dashboard_service import user_dashboard_service
from backend.core.security import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=APIResponse)
async def get_user_dashboard(current_user_id: str = Depends(get_current_user)):
    """Get user dashboard data"""
    
    result = await user_dashboard_service.get_user_dashboard(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch dashboard data")
        )

@router.get("/accounts", response_model=APIResponse)
async def get_user_accounts(current_user_id: str = Depends(get_current_user)):
    """Get user's linked accounts"""
    
    result = await user_dashboard_service.get_user_accounts(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Accounts retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch accounts"
        )

@router.get("/portfolio", response_model=APIResponse)
async def get_user_portfolio(current_user_id: str = Depends(get_current_user)):
    """Get user portfolio with trade history"""
    
    result = await user_dashboard_service.get_user_portfolio(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolio"
        )

@router.get("/profile", response_model=APIResponse)
async def get_user_profile(current_user_id: str = Depends(get_current_user)):
    """Get user profile information"""
    
    result = await user_service.get_user_by_id(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Profile retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/profile", response_model=APIResponse)
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """Update user profile"""
    
    result = await user_service.update_user(
        current_user_id, 
        profile_data.dict(exclude_unset=True), 
        current_user_id
    )
    
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

@router.put("/change-password", response_model=APIResponse)
async def change_password(
    password_data: PasswordChange,
    current_user_id: str = Depends(get_current_user)
):
    """Change user password"""
    
    result = await user_service.change_password(
        current_user_id,
        password_data.current_password,
        password_data.new_password
    )
    
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