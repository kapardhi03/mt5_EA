"""
User Panel API Endpoints
Handles all user-specific functionality including dashboard, accounts, portfolio, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Dict, List, Optional
import os
from datetime import datetime

from ..models.responses import APIResponse
from ..services.mongodb_service import mongodb_service
from ..core.auth import get_current_user, verify_user_role
from ..services.realtime_service import realtime_service

router = APIRouter(prefix="/api/v1/user", tags=["User Panel"])


@router.get("/dashboard", response_model=APIResponse)
async def get_user_dashboard(current_user_id: str = Depends(get_current_user)):
    """Get user dashboard data"""
    try:
        result = await mongodb_service.get_user_dashboard_data(current_user_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Dashboard data retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts", response_model=APIResponse)
async def get_user_accounts(current_user_id: str = Depends(get_current_user)):
    """Get all trading accounts for current user"""
    try:
        result = await mongodb_service.get_user_accounts(current_user_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Accounts retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts", response_model=APIResponse)
async def create_trading_account(
    account_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Create a new trading account"""
    try:
        # Add user_id to account data
        account_data["user_id"] = current_user_id

        result = await mongodb_service.create_trading_account(account_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio", response_model=APIResponse)
async def get_user_portfolio(current_user_id: str = Depends(get_current_user)):
    """Get user portfolio including trade history and PnL"""
    try:
        # Get user's accounts
        accounts_result = await mongodb_service.get_user_accounts(current_user_id)
        if not accounts_result["status"]:
            raise HTTPException(status_code=500, detail="Failed to fetch accounts")

        accounts = accounts_result["data"]["accounts"]

        # Mock portfolio data - in real implementation, fetch from trades collection
        portfolio_data = {
            "accounts": accounts,
            "trade_history": [
                {
                    "id": "trade_001",
                    "symbol": "EURUSD",
                    "type": "BUY",
                    "volume": 0.1,
                    "open_price": 1.0850,
                    "close_price": 1.0875,
                    "profit": 25.0,
                    "open_time": "2025-09-27T10:30:00Z",
                    "close_time": "2025-09-27T14:15:00Z",
                    "status": "closed"
                },
                {
                    "id": "trade_002",
                    "symbol": "GBPUSD",
                    "type": "SELL",
                    "volume": 0.2,
                    "open_price": 1.2650,
                    "close_price": None,
                    "profit": -15.0,
                    "open_time": "2025-09-28T08:00:00Z",
                    "close_time": None,
                    "status": "open"
                }
            ],
            "daily_pnl": [
                {"date": "2025-09-26", "pnl": 50.0},
                {"date": "2025-09-27", "pnl": 25.0},
                {"date": "2025-09-28", "pnl": -15.0}
            ],
            "weekly_pnl": [
                {"week": "2025-W38", "pnl": 150.0},
                {"week": "2025-W39", "pnl": 60.0}
            ],
            "net_return": {
                "total_return": 210.0,
                "return_percentage": 4.2,
                "copy_start_date": "2025-09-01T00:00:00Z"
            }
        }

        return APIResponse(
            success=True,
            message="Portfolio data retrieved successfully",
            data=portfolio_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=APIResponse)
async def get_user_profile(current_user_id: str = Depends(get_current_user)):
    """Get user profile information"""
    try:
        result = await mongodb_service.get_user_by_id(current_user_id)

        if result["status"]:
            profile_data = result["data"]
            # Remove sensitive information
            if "password_hash" in profile_data:
                del profile_data["password_hash"]

            return APIResponse(
                success=True,
                message="Profile retrieved successfully",
                data=profile_data
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=APIResponse)
async def update_user_profile(
    profile_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Update user profile information"""
    try:
        # Remove fields that shouldn't be updated via this endpoint
        restricted_fields = ["password_hash", "role", "status", "email_verified", "mobile_verified"]
        for field in restricted_fields:
            if field in profile_data:
                del profile_data[field]

        profile_data["updated_at"] = datetime.now()

        # Update user profile
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        result = await db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": profile_data}
        )

        if result.modified_count > 0:
            return APIResponse(
                success=True,
                message="Profile updated successfully"
            )
        else:
            return APIResponse(
                success=False,
                message="No changes made to profile"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/support/tickets", response_model=APIResponse)
async def get_user_support_tickets(current_user_id: str = Depends(get_current_user)):
    """Get support tickets for current user"""
    try:
        result = await mongodb_service.get_user_support_tickets(current_user_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Support tickets retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/support/tickets", response_model=APIResponse)
async def create_support_ticket(
    ticket_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Create a new support ticket"""
    try:
        ticket_data["user_id"] = current_user_id

        result = await mongodb_service.create_support_ticket(ticket_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ib-change", response_model=APIResponse)
async def upload_ib_change_proof(
    file: UploadFile = File(...),
    account_id: str = None,
    current_user_id: str = Depends(get_current_user)
):
    """Upload IB change proof for account"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPG, JPEG, PDF allowed.")

        # Create upload directory if it doesn't exist
        upload_dir = "uploads/ib_proofs"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{current_user_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)

        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Update user record with IB proof information
        db = mongodb_service.get_db()
        if db:
            from bson import ObjectId
            await db.users.update_one(
                {"_id": ObjectId(current_user_id)},
                {"$set": {
                    "ib_proof_filename": filename,
                    "ib_proof_upload_date": datetime.now(),
                    "ib_status": "pending",
                    "status": "pending_ib_change",
                    "updated_at": datetime.now()
                }}
            )

        # Send real-time notification to all admins about new IB proof upload
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        await realtime_service.notify_admins(
            "new_ib_proof",
            {
                "message": f"New IB proof uploaded by {user.get('name', 'Unknown')}",
                "user_id": current_user_id,
                "user_name": user.get("name", "Unknown"),
                "filename": filename,
                "uploaded_at": datetime.now().isoformat()
            }
        )

        return APIResponse(
            success=True,
            message="IB change proof uploaded successfully",
            data={"file_path": file_path}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ib-guides/{broker}", response_model=APIResponse)
async def get_ib_change_guide(broker: str):
    """Get IB change guide for specific broker"""
    try:
        guides = {
            "exness": {
                "title": "Exness IB Change Guide",
                "steps": [
                    "Login to your Exness Personal Area",
                    "Go to 'Partner' or 'IB' section",
                    "Enter new Partner ID: YOUR_NEW_PARTNER_ID",
                    "Verify with OTP sent to your registered mobile/email",
                    "Confirm the change",
                    "Take screenshot of confirmation page"
                ],
                "video_url": "https://example.com/exness-ib-change-guide",
                "support_email": "support@exness.com"
            },
            "vantage": {
                "title": "Vantage Markets IB Change Guide",
                "steps": [
                    "Prepare email template below",
                    "Send email to support@vantagemarkets.com",
                    "Include your account number and new IB ID",
                    "Wait for confirmation email",
                    "Forward confirmation email as proof"
                ],
                "email_template": "Subject: IB Change Request\n\nDear Vantage Support,\n\nI would like to change my IB for account: [YOUR_ACCOUNT_NUMBER]\nNew IB ID: [NEW_IB_ID]\n\nRegards,\n[YOUR_NAME]",
                "support_email": "support@vantagemarkets.com"
            }
        }

        if broker.lower() not in guides:
            raise HTTPException(status_code=404, detail="Guide not found for this broker")

        return APIResponse(
            success=True,
            message="IB change guide retrieved successfully",
            data=guides[broker.lower()]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/referral-links/{broker}", response_model=APIResponse)
async def get_referral_links(broker: str):
    """Get referral links for broker"""
    try:
        referral_links = {
            "exness": {
                "broker": "Exness",
                "register_url": "https://one.exness.link/a/your_referral_code",
                "description": "Open a new Exness account with our partnership",
                "bonus_info": "Get up to $100 welcome bonus"
            },
            "vantage": {
                "broker": "Vantage Markets",
                "register_url": "https://www.vantagemarkets.com/?cxd=your_referral_code",
                "description": "Join Vantage Markets with our IB partnership",
                "bonus_info": "Get competitive spreads and bonuses"
            }
        }

        if broker.lower() not in referral_links:
            raise HTTPException(status_code=404, detail="Referral link not found for this broker")

        return APIResponse(
            success=True,
            message="Referral link retrieved successfully",
            data=referral_links[broker.lower()]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ib-status", response_model=APIResponse)
async def get_ib_status(current_user_id: str = Depends(get_current_user)):
    """Get current user's IB change status"""
    try:
        db = mongodb_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")

        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        ib_status_data = {
            "ib_status": user.get("ib_status", "not_changed"),
            "ib_proof_filename": user.get("ib_proof_filename"),
            "ib_proof_upload_date": user.get("ib_proof_upload_date"),
            "ib_approval_date": user.get("ib_approval_date"),
            "ib_approved_by": user.get("ib_approved_by"),
            "ib_rejection_reason": user.get("ib_rejection_reason"),
            "user_status": user.get("status"),
            "ea_enabled": user.get("ib_status") == "approved"
        }

        return APIResponse(
            success=True,
            message="IB status retrieved successfully",
            data=ib_status_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))