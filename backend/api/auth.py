# ===================================
# api/auth.py
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.user import UserRegistration, UserLogin, OTPRequest, OTPVerification, TokenResponse, IBProofUpload, IBProofAction
from backend.models.common import APIResponse
from backend.services.mongodb_service import mongodb_service
from backend.services.real_sms_service import real_sms_service
from backend.services.otp_service import otp_service
from backend.services.email_service import email_service
from backend.core.security import get_current_user, create_access_token
import secrets
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=APIResponse)
async def register(user_data: UserRegistration):
    """Register a new user with complete data storage"""
    try:
        # Create user in database with all registration data
        result = await mongodb_service.create_user(user_data.dict())

        if result["status"]:
            # Send welcome email
            try:
                await email_service.send_welcome_email(user_data.email, user_data.name)
            except Exception as e:
                print(f"Warning: Failed to send welcome email: {str(e)}")

            # Also create an access token for the newly registered user so frontend can authenticate
            user_id = result.get("data", {}).get("user_id")
            access_token = None
            if user_id:
                try:
                    access_token = create_access_token(user_id)
                except Exception:
                    access_token = None

            response_data = result.get("data", {})
            if access_token:
                response_data.update({"access_token": access_token, "token_type": "bearer"})

            return APIResponse(
                success=True,
                message=result["message"],
                data=response_data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=APIResponse)
async def login(login_data: UserLogin):
    """Login user"""
    result = await mongodb_service.authenticate_user(
        login_data.mobile_or_email,
        login_data.password
    )

    if result["status"]:
        # Generate access token
        access_token = create_access_token(result["data"]["id"])

        user_data = result["data"]
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }

        return APIResponse(
            success=True,
            message=result["message"],
            data=response_data
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )

@router.post("/send-otp", response_model=APIResponse)
async def send_otp(otp_request: OTPRequest):
    """Send OTP for verification using integrated services"""
    try:
        # Use the integrated OTP service
        result = await otp_service.send_otp(
            otp_request.mobile_or_email,
            otp_request.otp_type,
            "verification"
        )

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data=result.get("data")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=APIResponse)
async def verify_otp(otp_data: OTPVerification):
    """Verify OTP using integrated service"""
    try:
        result = await otp_service.verify_otp(
            otp_data.mobile_or_email,
            otp_data.otp,
            otp_data.otp_type
        )

        if result["status"]:
            return APIResponse(success=True, message=result["message"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )

@router.get("/me", response_model=APIResponse)
async def get_current_user_info(current_user_id: str = Depends(get_current_user)):
    """Get current user information"""
    result = await mongodb_service.get_user_by_id(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="User information retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.post("/activate-user", response_model=APIResponse)
async def activate_user_directly(activation_data: dict):
    """Activate a user directly (temporary admin function)"""
    try:
        email = activation_data.get("email")
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

@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(request_data: dict):
    """Initiate password reset process"""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Generate reset token and send email/SMS
        result = await mongodb_service.create_password_reset_token(email)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Password reset token sent successfully",
                data={"reset_token": result["data"]["reset_token"]}  # In demo mode, return token
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password", response_model=APIResponse)
async def reset_password(reset_data: dict):
    """Reset password using token"""
    try:
        email = reset_data.get("email")
        reset_token = reset_data.get("reset_token")
        new_password = reset_data.get("new_password")

        if not all([email, reset_token, new_password]):
            raise HTTPException(status_code=400, detail="Email, reset token, and new password are required")

        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        result = await mongodb_service.reset_password_with_token(email, reset_token, new_password)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin-reset-password", response_model=APIResponse)
async def admin_reset_password(reset_data: dict):
    """Admin endpoint to directly reset any user's password"""
    try:
        email = reset_data.get("email")
        new_password = reset_data.get("new_password", "admin12345")  # Default admin password

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        result = await mongodb_service.admin_reset_password(email, new_password)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={"email": email, "new_password": new_password}
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-role", response_model=APIResponse)
async def update_user_role(role_data: dict):
    """Update user role (temporary admin function)"""
    try:
        email = role_data.get("email")
        new_role = role_data.get("role", "admin")

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await mongodb_service.update_user_role_by_email(email, new_role)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-ib-proof", response_model=APIResponse)
async def upload_ib_proof(ib_data: IBProofUpload, current_user_id: str = Depends(get_current_user)):
    """Upload IB proof image and update user details"""
    try:
        # Get user details for email notification
        user_result = await mongodb_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_result["data"]
        
        # Update user with IB proof and broker details
        update_data = {
            "broker": ib_data.broker,
            "account_no": ib_data.account_number,
            "trading_password_hash": ib_data.trading_password,  # In production, hash this
            "ib_proof_image_data": ib_data.proof_image,
            "ib_proof_filename": ib_data.proof_filename if hasattr(ib_data, 'proof_filename') else None,
            "ib_status": "pending",
            "ib_proof_upload_date": datetime.now(),
            "status": "pending_ib_change"
        }

        result = await mongodb_service.update_user_ib_proof(current_user_id, update_data)

        if result["status"]:
            # Send notification email to user
            try:
                await email_service.send_ib_approval_email(
                    user_data["email"], 
                    user_data["name"], 
                    "pending"
                )
            except Exception as e:
                print(f"Warning: Failed to send IB notification email: {str(e)}")
            return APIResponse(
                success=True,
                message="IB proof uploaded successfully. Waiting for admin approval.",
                data={"ib_status": "pending"}
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))