"""
Registration Flow API Endpoints
Handles the 5-step registration process for copy-trading platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import secrets
import string
from bson import ObjectId

from ..models.responses import APIResponse
from ..services.mongodb_service import mongodb_service
from ..core.auth import get_current_user
from ..models.copy_trading_models import UserRole, UserStatus, AccountType

router = APIRouter(prefix="/api/v1/registration", tags=["Registration"])


@router.post("/step1/basic-info", response_model=APIResponse)
async def registration_step1(user_data: Dict):
    """Step 1: Basic Information (Name, Email, Mobile, Password)"""
    try:
        # Validate required fields
        required_fields = ["name", "email", "mobile", "password"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Check if user already exists
        existing_user = await mongodb_service.get_user_by_email(user_data["email"])
        if existing_user["status"]:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create temporary user record
        temp_user_data = {
            "name": user_data["name"],
            "email": user_data["email"],
            "mobile": user_data["mobile"],
            "password": user_data["password"],
            "role": UserRole.USER,
            "status": UserStatus.PENDING,
            "registration_step": 1,
            "registration_token": secrets.token_urlsafe(32),
            "registration_expires": datetime.now() + timedelta(hours=24),
            "created_at": datetime.now()
        }

        result = await mongodb_service.create_temp_user(temp_user_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Step 1 completed successfully",
                data={
                    "registration_token": temp_user_data["registration_token"],
                    "step": 1,
                    "next_step": "personal-details"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step2/personal-details", response_model=APIResponse)
async def registration_step2(personal_data: Dict):
    """Step 2: Personal Details (Address, Country, State, City, PIN)"""
    try:
        registration_token = personal_data.get("registration_token")
        if not registration_token:
            raise HTTPException(status_code=400, detail="Registration token required")

        # Get temp user
        temp_user = await mongodb_service.get_temp_user_by_token(registration_token)
        if not temp_user["status"]:
            raise HTTPException(status_code=400, detail="Invalid or expired registration token")

        # Update with personal details
        update_data = {
            "address": personal_data.get("address"),
            "country": personal_data.get("country"),
            "state": personal_data.get("state"),
            "city": personal_data.get("city"),
            "pin_code": personal_data.get("pin_code"),
            "registration_step": 2,
            "updated_at": datetime.now()
        }

        result = await mongodb_service.update_temp_user(registration_token, update_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Step 2 completed successfully",
                data={
                    "registration_token": registration_token,
                    "step": 2,
                    "next_step": "account-details"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step3/account-details", response_model=APIResponse)
async def registration_step3(account_data: Dict):
    """Step 3: Trading Account Details (Broker, Server, Account Number, etc.)"""
    try:
        registration_token = account_data.get("registration_token")
        if not registration_token:
            raise HTTPException(status_code=400, detail="Registration token required")

        # Validate required account fields
        required_fields = ["broker", "server", "account_number", "account_type", "trading_password"]
        for field in required_fields:
            if field not in account_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Get temp user
        temp_user = await mongodb_service.get_temp_user_by_token(registration_token)
        if not temp_user["status"]:
            raise HTTPException(status_code=400, detail="Invalid or expired registration token")

        # Update with account details
        update_data = {
            "trading_account": {
                "broker": account_data["broker"],
                "server": account_data["server"],
                "account_number": account_data["account_number"],
                "account_type": account_data["account_type"],
                "trading_password": account_data["trading_password"],
                "leverage": account_data.get("leverage", 1000),
                "currency": account_data.get("currency", "USD")
            },
            "registration_step": 3,
            "updated_at": datetime.now()
        }

        result = await mongodb_service.update_temp_user(registration_token, update_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Step 3 completed successfully",
                data={
                    "registration_token": registration_token,
                    "step": 3,
                    "next_step": "group-selection"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-groups", response_model=APIResponse)
async def get_available_groups():
    """Get list of available trading groups for registration"""
    try:
        result = await mongodb_service.get_available_trading_groups()

        if result["status"]:
            return APIResponse(
                success=True,
                message="Available groups retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step4/group-selection", response_model=APIResponse)
async def registration_step4(group_data: Dict):
    """Step 4: Select Trading Group"""
    try:
        registration_token = group_data.get("registration_token")
        group_id = group_data.get("group_id")

        if not registration_token or not group_id:
            raise HTTPException(status_code=400, detail="Registration token and group_id required")

        # Get temp user
        temp_user = await mongodb_service.get_temp_user_by_token(registration_token)
        if not temp_user["status"]:
            raise HTTPException(status_code=400, detail="Invalid or expired registration token")

        # Validate group exists and is accepting members
        group_result = await mongodb_service.get_group_by_id(group_id)
        if not group_result["status"]:
            raise HTTPException(status_code=400, detail="Invalid group selected")

        # Update with group selection
        update_data = {
            "selected_group_id": group_id,
            "registration_step": 4,
            "updated_at": datetime.now()
        }

        result = await mongodb_service.update_temp_user(registration_token, update_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Step 4 completed successfully",
                data={
                    "registration_token": registration_token,
                    "step": 4,
                    "next_step": "verification",
                    "group_info": group_result["data"]
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step5/verification", response_model=APIResponse)
async def registration_step5(verification_data: Dict):
    """Step 5: OTP Verification and Final Registration"""
    try:
        registration_token = verification_data.get("registration_token")
        otp = verification_data.get("otp")

        if not registration_token or not otp:
            raise HTTPException(status_code=400, detail="Registration token and OTP required")

        # Get temp user
        temp_user_result = await mongodb_service.get_temp_user_by_token(registration_token)
        if not temp_user_result["status"]:
            raise HTTPException(status_code=400, detail="Invalid or expired registration token")

        temp_user = temp_user_result["data"]

        # Verify OTP (In production, implement proper OTP verification)
        if otp != "123456":  # Demo OTP for testing
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Create final user account
        user_data = {
            "name": temp_user["name"],
            "email": temp_user["email"],
            "mobile": temp_user["mobile"],
            "password": temp_user["password"],
            "role": UserRole.USER,
            "status": UserStatus.PENDING,
            "address": temp_user.get("address"),
            "country": temp_user.get("country"),
            "state": temp_user.get("state"),
            "city": temp_user.get("city"),
            "pin_code": temp_user.get("pin_code"),
            "group_id": temp_user["selected_group_id"],
            "group_join_date": datetime.now(),
            "email_verified": True,
            "mobile_verified": True,
            "kyc_status": "pending"
        }

        # Create user
        user_result = await mongodb_service.create_user(user_data)
        if not user_result["status"]:
            raise HTTPException(status_code=400, detail=user_result["message"])

        user_id = user_result["data"]["user_id"]

        # Create trading account
        trading_account = temp_user["trading_account"]
        trading_account["user_id"] = user_id
        trading_account["group_id"] = temp_user["selected_group_id"]
        trading_account["status"] = "pending"

        account_result = await mongodb_service.create_trading_account(trading_account)

        # Clean up temp user
        await mongodb_service.delete_temp_user(registration_token)

        return APIResponse(
            success=True,
            message="Registration completed successfully! Your account is pending approval.",
            data={
                "user_id": user_id,
                "account_id": account_result["data"]["account_id"] if account_result["status"] else None,
                "status": "pending_approval",
                "next_steps": [
                    "Wait for admin approval",
                    "Check email for approval notification",
                    "Complete IB change if required"
                ]
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resend-otp", response_model=APIResponse)
async def resend_otp(token_data: Dict):
    """Resend OTP for verification"""
    try:
        registration_token = token_data.get("registration_token")
        if not registration_token:
            raise HTTPException(status_code=400, detail="Registration token required")

        # Get temp user
        temp_user_result = await mongodb_service.get_temp_user_by_token(registration_token)
        if not temp_user_result["status"]:
            raise HTTPException(status_code=400, detail="Invalid or expired registration token")

        # In production, send actual OTP via SMS/Email
        # For demo, we'll just return success
        return APIResponse(
            success=True,
            message="OTP sent successfully",
            data={"otp_sent": True, "demo_otp": "123456"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{registration_token}", response_model=APIResponse)
async def get_registration_status(registration_token: str):
    """Get current registration status"""
    try:
        result = await mongodb_service.get_temp_user_by_token(registration_token)

        if result["status"]:
            temp_user = result["data"]
            return APIResponse(
                success=True,
                message="Registration status retrieved",
                data={
                    "current_step": temp_user.get("registration_step", 1),
                    "email": temp_user["email"],
                    "name": temp_user["name"],
                    "expires_at": temp_user.get("registration_expires")
                }
            )
        else:
            raise HTTPException(status_code=404, detail="Registration not found or expired")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))