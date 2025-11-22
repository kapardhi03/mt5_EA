# ===================================
# Simple admin endpoints that work with real database
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models.common import APIResponse
from backend.services.mongodb_service import mongodb_service
from backend.core.security import get_current_user
from typing import Optional
from datetime import datetime

router = APIRouter()

async def verify_admin_simple(current_user_id: str = Depends(get_current_user)):
    """Simple admin verification using mongodb_service directly"""
    user_result = await mongodb_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return user

@router.get("/users", response_model=APIResponse)
async def get_all_users(admin_user = Depends(verify_admin_simple)):
    """Get all users from database"""
    try:
        result = await mongodb_service.get_all_users()

        if result["status"]:
            return APIResponse(
                success=True,
                message="Users retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.post("/activate-user", response_model=APIResponse)
async def activate_user_by_email(request_data: dict, admin_user = Depends(verify_admin_simple)):
    """Activate user by email"""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await mongodb_service.activate_user_by_email(email)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-user-role", response_model=APIResponse)
async def update_user_role_by_email(request_data: dict, admin_user = Depends(verify_admin_simple)):
    """Update user role by email"""
    try:
        email = request_data.get("email")
        role = request_data.get("role", "user")

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await mongodb_service.update_user_role_by_email(email, role)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suspend-user", response_model=APIResponse)
async def suspend_user_by_email(request_data: dict, admin_user = Depends(verify_admin_simple)):
    """Suspend user by email"""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await mongodb_service.update_user_status_by_email(email, "inactive")

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reactivate-user", response_model=APIResponse)
async def reactivate_user_by_email(request_data: dict, admin_user = Depends(verify_admin_simple)):
    """Reactivate user by email"""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await mongodb_service.update_user_status_by_email(email, "active")

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}", response_model=APIResponse)
async def delete_user(user_id: str, admin_user = Depends(verify_admin_simple)):
    """Delete a suspended user and related records"""
    try:
        result = await mongodb_service.delete_user_permanently(user_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data=result.get("data")
            )

        detail = result.get("message", "Failed to delete user")
        if "not found" in detail.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}", response_model=APIResponse)
async def edit_user(user_id: str, updates: dict, admin_user = Depends(verify_admin_simple)):
    """Update editable user fields"""
    try:
        result = await mongodb_service.update_user_details(user_id, updates)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data=result.get("data")
            )

        detail = result.get("message", "Failed to update user")
        if "not found" in detail.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-user", response_model=APIResponse)
async def create_user_simple(request_data: dict, admin_user = Depends(verify_admin_simple)):
    """Create a new user (admin only)"""
    try:
        # Extract required fields
        name = request_data.get("name")
        email = request_data.get("email")
        mobile = request_data.get("mobile")
        password = request_data.get("password")
        role = request_data.get("role", "user")
        country = request_data.get("country", "India")
        state = request_data.get("state", "Unknown")
        city = request_data.get("city", "Unknown")
        pin_code = request_data.get("pin_code", "000000")

        # Validate required fields
        if not all([name, email, mobile, password]):
            raise HTTPException(status_code=400, detail="Name, email, mobile, and password are required")

        # Check if user already exists
        existing_user = await mongodb_service.get_user_by_email(email)
        if existing_user["status"]:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create user data matching your schema
        user_data = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": password,  # Will be hashed by create_user function
            "role": role,
            "status": "active",  # Auto-activate admin-created users
            "country": country,
            "state": state,
            "city": city,
            "pin_code": pin_code,
            "mobile_verified": True,
            "email_verified": False,  # Admin can verify later
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_login": None
        }

        result = await mongodb_service.create_user(user_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message="User created successfully",
                data=result.get("data")
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=APIResponse)
async def get_admin_dashboard(admin_user = Depends(verify_admin_simple)):
    """Get admin dashboard stats"""
    try:
        # Get real stats from database
        users_result = await mongodb_service.get_all_users()
        users = users_result.get("data", []) if users_result["status"] else []

        dashboard_data = {
            "total_users": len(users),
            "active_users": len([u for u in users if u.get("status") == "active"]),
            "pending_users": len([u for u in users if u.get("status") == "pending"]),
            "suspended_users": len([u for u in users if u.get("status") == "suspended"]),
            "admin_users": len([u for u in users if u.get("role") == "admin"]),
            "regular_users": len([u for u in users if u.get("role") == "user"]),
            "master_users": len([u for u in users if u.get("role") == "master"]),
            "recent_registrations": len([u for u in users if u.get("created_at") and
                                       (datetime.now() - u["created_at"]).days <= 7]),
        }

        return APIResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )