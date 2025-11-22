"""
Group Panel API Endpoints
Handles group leader/sub-admin functionality for managing their specific group
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId

from ..models.responses import APIResponse
from ..services.mongodb_service import mongodb_service
from ..core.auth import get_current_user, verify_group_leader

router = APIRouter(prefix="/api/v1/group", tags=["Group Panel"])


@router.get("/dashboard", response_model=APIResponse)
async def get_group_dashboard(current_user_id: str = Depends(get_current_user)):
    """Get group dashboard data for group leader"""
    try:
        # Get user's group
        user_result = await mongodb_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=404, detail="User not found")

        user = user_result["data"]

        # Check if user is a group leader
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])
        result = await mongodb_service.get_group_dashboard_data(group_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Group dashboard data retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members", response_model=APIResponse)
async def get_group_members(current_user_id: str = Depends(get_current_user)):
    """Get all members in the group"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])

        # Get all accounts in this group
        accounts_cursor = db.trading_accounts.find({"group_id": group_id})
        accounts = await accounts_cursor.to_list(length=None)

        # Get user details for each account
        members = []
        for account in accounts:
            user_result = await mongodb_service.get_user_by_id(account["user_id"])
            if user_result["status"]:
                user = user_result["data"]
                member_data = {
                    "account_id": str(account["_id"]),
                    "user_id": account["user_id"],
                    "name": user["name"],
                    "email": user["email"],
                    "mobile": user["mobile"],
                    "broker": account["broker"],
                    "server": account["server"],
                    "account_number_masked": "*" * (len(account["account_number"]) - 4) + account["account_number"][-4:],
                    "account_type": account.get("account_type", ""),
                    "copy_status": account.get("copy_status", "pending"),
                    "copy_start_date": account.get("copy_start_date"),
                    "opening_balance": account.get("opening_balance", 0),
                    "current_balance": account.get("current_balance", 0),
                    "profit_since_copy_start": account.get("profit_since_copy_start", 0),
                    "running_trades_count": account.get("running_trades_count", 0),
                    "status": account.get("status", "pending"),
                    "join_date": user.get("group_join_date"),
                    "last_sync": account.get("last_sync"),
                    "last_error": account.get("last_error")
                }
                members.append(member_data)

        return APIResponse(
            success=True,
            message="Group members retrieved successfully",
            data={"members": members, "group_name": group["group_name"]}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/members/{account_id}/approve", response_model=APIResponse)
async def approve_group_member(
    account_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Approve a pending member in the group"""
    try:
        # Verify user is group leader
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])

        # Approve the account
        result = await mongodb_service.update_account_status(account_id, "approved", group_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/members/{account_id}/reject", response_model=APIResponse)
async def reject_group_member(
    account_id: str,
    rejection_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Reject a pending member in the group"""
    try:
        # Verify user is group leader
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        # Reject the account
        await db.trading_accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": {
                "status": "rejected",
                "rejection_reason": rejection_data.get("reason", "No reason provided"),
                "rejected_at": datetime.now(),
                "updated_at": datetime.now()
            }}
        )

        return APIResponse(
            success=True,
            message="Member rejected successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trading-controls", response_model=APIResponse)
async def get_trading_controls(current_user_id: str = Depends(get_current_user)):
    """Get current trading controls for the group"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        trading_controls = {
            "group_id": str(group["_id"]),
            "group_name": group["group_name"],
            "trading_status": group.get("trading_status", "active"),
            "auto_pause_rules": group.get("auto_pause_rules", {}),
            "last_updated": group.get("updated_at"),
            "api_key_status": group.get("api_key_status", "inactive")
        }

        return APIResponse(
            success=True,
            message="Trading controls retrieved successfully",
            data=trading_controls
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading-controls/toggle", response_model=APIResponse)
async def toggle_group_trading(
    control_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Start/Stop group trading (requires OTP in production)"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])
        new_status = control_data.get("status", "active")  # active, paused, stopped

        # In production, verify OTP here
        # otp = control_data.get("otp")
        # if not verify_otp(current_user_id, otp):
        #     raise HTTPException(status_code=400, detail="Invalid OTP")

        result = await mongodb_service.update_group_trading_status(group_id, new_status, current_user_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settlements", response_model=APIResponse)
async def get_group_settlements(current_user_id: str = Depends(get_current_user)):
    """Get settlements for the group"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])
        result = await mongodb_service.get_settlements(group_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Settlements retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settlements", response_model=APIResponse)
async def create_settlement_request(
    settlement_data: Dict,
    current_user_id: str = Depends(get_current_user)
):
    """Create a new settlement request"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])
        settlement_data["group_id"] = group_id
        settlement_data["submitted_by"] = current_user_id

        result = await mongodb_service.create_settlement(settlement_data)

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


@router.get("/reports/members", response_model=APIResponse)
async def get_group_member_reports(current_user_id: str = Depends(get_current_user)):
    """Get profit sharing reports for group members"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])

        # Get all accounts in this group with profit data
        accounts_cursor = db.trading_accounts.find({"group_id": group_id, "status": "approved"})
        accounts = await accounts_cursor.to_list(length=None)

        member_reports = []
        for account in accounts:
            user_result = await mongodb_service.get_user_by_id(account["user_id"])
            if user_result["status"]:
                user = user_result["data"]

                profit_since_start = account.get("profit_since_copy_start", 0)
                profit_sharing_percentage = group.get("profit_sharing_percentage", 80)
                member_share = profit_since_start * (profit_sharing_percentage / 100)

                report_data = {
                    "user_name": user["name"],
                    "account_number_masked": "*" * (len(account["account_number"]) - 4) + account["account_number"][-4:],
                    "copy_start_date": account.get("copy_start_date"),
                    "opening_balance": account.get("opening_balance", 0),
                    "current_balance": account.get("current_balance", 0),
                    "total_profit": profit_since_start,
                    "profit_sharing_percentage": profit_sharing_percentage,
                    "member_share": member_share,
                    "company_share": profit_since_start - member_share,
                    "last_settlement": account.get("last_settlement_date"),
                    "pending_amount": member_share  # Simplified calculation
                }
                member_reports.append(report_data)

        return APIResponse(
            success=True,
            message="Member reports retrieved successfully",
            data={"reports": member_reports, "group_name": group["group_name"]}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/errors", response_model=APIResponse)
async def get_group_error_reports(current_user_id: str = Depends(get_current_user)):
    """Get error reports for the group"""
    try:
        # Get user's group
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        group = await db.trading_groups.find_one({"group_leader_id": current_user_id})
        if not group:
            raise HTTPException(status_code=403, detail="User is not a group leader")

        group_id = str(group["_id"])
        result = await mongodb_service.get_error_logs(group_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message="Error reports retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))