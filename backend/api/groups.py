"""
Working Groups API - Complete CRUD operations with MongoDB
"""
from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.common import APIResponse
from backend.services.mongodb_service import mongodb_service
from backend.services.realtime_service import realtime_service
from backend.core.security import get_current_user
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import secrets
from bson import ObjectId

router = APIRouter()

# Request Models
class GroupCreateRequest(BaseModel):
    group_name: str = Field(..., min_length=3, max_length=100)
    company_name: str = Field(..., min_length=3, max_length=100)
    profit_sharing_percentage: int = Field(..., ge=10, le=100)
    settlement_cycle: str = Field(..., description="daily, weekly, or monthly")
    grace_days: int = Field(default=2, ge=0, le=30)

class JoinGroupRequest(BaseModel):
    referral_code: str = Field(..., description="Group referral code or API key")
    account_number: str
    broker: str
    account_type: str
    server: str
    password: str
    investor_password: Optional[str] = None


class JoinByApiKeyRequest(BaseModel):
    api_key: str = Field(..., description="Group API key")

async def verify_admin_or_manager(current_user_id: str = Depends(get_current_user)):
    """Verify user is admin or group manager"""
    db = mongodb_service.get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    user = await db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] not in ["admin", "group_manager"]:
        raise HTTPException(status_code=403, detail="Admin or Group Manager access required")

    return user

@router.post("/create", response_model=APIResponse)
async def create_group(
    group_data: GroupCreateRequest,
    current_user = Depends(verify_admin_or_manager)
):
    """Create a new trading group with API key"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Check if group name already exists
        existing_group = await db.groups.find_one({"group_name": group_data.group_name})
        if existing_group:
            raise HTTPException(status_code=400, detail="Group name already exists")

        # Generate API key and referral code
        api_key = f"mt5_api_{secrets.token_urlsafe(32)}"
        referral_code = f"REF_{secrets.token_urlsafe(16).upper()}"

        # Create group document
        group_doc = {
            "group_name": group_data.group_name,
            "company_name": group_data.company_name,
            "profit_sharing_percentage": group_data.profit_sharing_percentage,
            "settlement_cycle": group_data.settlement_cycle,
            "grace_days": group_data.grace_days,
            "master_accounts": [],
            "api_key": api_key,
            "referral_code": referral_code,
            "trading_status": "active",
            "created_by": str(current_user["_id"]),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_members": 0,
            "active_members": 0,
            "total_equity": 0.0,
            "total_profit": 0.0,
            "pending_settlement": 0.0,
            "last_settlement_date": None,
            "next_settlement_date": None
        }

        # Insert group
        result = await db.groups.insert_one(group_doc)
        group_id = str(result.inserted_id)

        return APIResponse(
            success=True,
            message="Group created successfully",
            data={
                "group_id": group_id,
                "group_name": group_data.group_name,
                "api_key": api_key,
                "referral_code": referral_code,
                "referral_link": f"/groups/join?ref={referral_code}",
                "trading_status": "active"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating group: {str(e)}")

@router.get("/list", response_model=APIResponse)
async def list_groups(
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user_id: str = Depends(get_current_user)
):
    """List all groups with optional filters"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Build query
        query = {}
        if status and status != "all":
            query["trading_status"] = status
        if search:
            query["$or"] = [
                {"group_name": {"$regex": search, "$options": "i"}},
                {"company_name": {"$regex": search, "$options": "i"}}
            ]

        # Get groups
        groups_cursor = db.groups.find(query)
        groups = await groups_cursor.to_list(length=None)

        # Format groups for response
        formatted_groups = []
        for group in groups:
            formatted_groups.append({
                "id": str(group["_id"]),
                "group_name": group["group_name"],
                "company_name": group["company_name"],
                "profit_sharing_percentage": group["profit_sharing_percentage"],
                "settlement_cycle": group["settlement_cycle"],
                "trading_status": group["trading_status"],
                "total_members": group.get("total_members", 0),
                "active_members": group.get("active_members", 0),
                "total_equity": group.get("total_equity", 0.0),
                "api_key": group["api_key"],
                "created_at": group["created_at"].isoformat() if group.get("created_at") else None
            })

        return APIResponse(
            success=True,
            message="Groups retrieved successfully",
            data={"groups": formatted_groups, "total": len(formatted_groups)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving groups: {str(e)}")

@router.patch("/{group_id}/status", response_model=APIResponse)
async def update_group_status(
    group_id: str,
    status_data: dict,
    current_user = Depends(verify_admin_or_manager)
):
    """Update group trading status"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        new_status = status_data.get("status")
        if new_status not in ["active", "paused", "suspended"]:
            raise HTTPException(status_code=400, detail="Invalid status")

        # Update group status
        result = await db.groups.update_one(
            {"_id": ObjectId(group_id)},
            {"$set": {"trading_status": new_status, "updated_at": datetime.now()}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        return APIResponse(
            success=True,
            message=f"Group status updated to {new_status}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating group status: {str(e)}")

@router.post("/join-by-referral", response_model=APIResponse)
async def join_group_by_referral(
    join_data: JoinGroupRequest,
    current_user_id: str = Depends(get_current_user)
):
    """Join a trading group using referral code or API key"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Find group by referral code or API key
        group = await db.groups.find_one({
            "$or": [
                {"referral_code": join_data.referral_code},
                {"api_key": join_data.referral_code}
            ]
        })

        if not group:
            raise HTTPException(status_code=404, detail="Invalid referral code or API key")

        group_id = str(group["_id"])

        # Check if user already belongs to ANY group (one group per user rule)
        existing_membership = await db.users.find_one({
            "_id": ObjectId(current_user_id),
            "group_id": {"$exists": True, "$ne": None}
        })

        # If user is already in a group, perform a graceful leave from that group
        if existing_membership:
            try:
                prev_group_id = existing_membership.get("group_id")
                # mark any member records as left
                if prev_group_id:
                    await db.members.update_many(
                        {"user_id": current_user_id, "group_id": prev_group_id, "status": {"$ne": "left"}},
                        {"$set": {"status": "left", "left_at": datetime.now()}}
                    )

                    # deactivate any trading accounts associated with the previous group
                    await db.trading_accounts.update_many(
                        {"user_id": current_user_id, "group_id": prev_group_id},
                        {"$set": {"status": "inactive", "updated_at": datetime.now()}}
                    )

                # remove group-related fields from users doc (we'll set the new group shortly)
                await db.users.update_one(
                    {"_id": ObjectId(current_user_id)},
                    {"$unset": {"group_id": "", "group_join_date": "", "referral_code_used": ""}, "$set": {"updated_at": datetime.now()}}
                )
            except Exception:
                # non-fatal: continue to attempt join; if DB operations fail the final join may still succeed
                pass

        # Check if user's IB status is approved
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.get("ib_status") != "approved":
            raise HTTPException(status_code=400, detail="IB change must be approved before joining a group")

        # Update user record with group membership
        await db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": {
                "group_id": group_id,
                "group_join_date": datetime.now(),
                "referral_code_used": join_data.referral_code,
                "updated_at": datetime.now()
            }}
        )

        # Send real-time notifications
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        user_name = user.get("name", "Unknown") if user else "Unknown"

        # Notify user about successful group join
        await realtime_service.notify_user(
            current_user_id,
            "group_joined",
            {
                "message": f"Successfully joined group: {group['group_name']}",
                "group_id": group_id,
                "group_name": group["group_name"],
                "join_date": datetime.now().isoformat()
            }
        )

        # Notify group masters about new member
        await realtime_service.notify_masters(
            "new_group_member",
            {
                "message": f"New member joined {group['group_name']}: {user_name}",
                "group_id": group_id,
                "group_name": group["group_name"],
                "user_id": current_user_id,
                "user_name": user_name,
                "join_date": datetime.now().isoformat()
            }
        )

        return APIResponse(
            success=True,
            message=f"Successfully joined group: {group['group_name']}",
            data={
                "group_id": group_id,
                "group_name": group["group_name"],
                "company_name": group["company_name"],
                "join_date": datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining group: {str(e)}")


@router.post("/join-by-api-key", response_model=APIResponse)
async def join_group_by_api_key(
    body: JoinByApiKeyRequest,
    current_user_id: str = Depends(get_current_user)
):
    """Join a trading group using only an API key (for users)"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Find group by API key
        group = await db.groups.find_one({"api_key": body.api_key})
        if not group:
            raise HTTPException(status_code=404, detail="Invalid API key")

        group_id = str(group["_id"])

        # Ensure user is not already in a group; if they are, gracefully leave that group first
        existing_membership = await db.users.find_one({
            "_id": ObjectId(current_user_id),
            "group_id": {"$exists": True, "$ne": None}
        })

        if existing_membership:
            try:
                prev_group_id = existing_membership.get("group_id")
                if prev_group_id:
                    await db.members.update_many(
                        {"user_id": current_user_id, "group_id": prev_group_id, "status": {"$ne": "left"}},
                        {"$set": {"status": "left", "left_at": datetime.now()}}
                    )
                    await db.trading_accounts.update_many(
                        {"user_id": current_user_id, "group_id": prev_group_id},
                        {"$set": {"status": "inactive", "updated_at": datetime.now()}}
                    )

                await db.users.update_one(
                    {"_id": ObjectId(current_user_id)},
                    {"$unset": {"group_id": "", "group_join_date": "", "referral_code_used": ""}, "$set": {"updated_at": datetime.now()}}
                )
            except Exception:
                pass

        # Check IB approval
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.get("ib_status") != "approved":
            raise HTTPException(status_code=400, detail="IB change must be approved before joining a group")

        # Update user record with group membership
        await db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": {
                "group_id": group_id,
                "group_join_date": datetime.now(),
                "referral_code_used": None,
                "updated_at": datetime.now()
            }}
        )

        # Notify via realtime service
        await realtime_service.notify_user(
            current_user_id,
            "group_joined",
            {
                "message": f"Successfully joined group: {group['group_name']}",
                "group_id": group_id,
                "group_name": group["group_name"],
                "join_date": datetime.now().isoformat()
            }
        )

        return APIResponse(
            success=True,
            message=f"Successfully joined group: {group['group_name']}",
            data={
                "group_id": group_id,
                "group_name": group["group_name"],
                "company_name": group["company_name"],
                "join_date": datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining group by api key: {str(e)}")


@router.post("/{group_id}/join", response_model=APIResponse)
async def join_group(
    group_id: str,
    join_data: JoinGroupRequest,
    current_user_id: str = Depends(verify_admin_or_manager)
):
    """[ADMIN ONLY] Join a trading group directly (bypasses referral requirement)"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Check if group exists
        group = await db.groups.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Check if user already a member
        existing_member = await db.members.find_one({
            "user_id": current_user_id,
            "group_id": group_id
        })
        if existing_member:
            raise HTTPException(status_code=400, detail="Already a member of this group")

        # Create trading account
        trading_account = {
            "user_id": current_user_id,
            "account_number": join_data.account_number,
            "account_type": join_data.account_type,
            "broker": join_data.broker,
            "server": join_data.server,
            "password_hash": mongodb_service._hash_password(join_data.password),
            "investor_password_hash": mongodb_service._hash_password(join_data.investor_password) if join_data.investor_password else None,
            "balance": 0.0,
            "equity": 0.0,
            "currency": "USD",
            "status": "pending",
            "group_id": group_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # Insert trading account
        account_result = await db.trading_accounts.insert_one(trading_account)
        account_id = str(account_result.inserted_id)

        # Create group membership
        member_doc = {
            "user_id": current_user_id,
            "group_id": group_id,
            "account_id": account_id,
            "status": "pending",
            "opening_balance": 0.0,
            "current_balance": 0.0,
            "profit_till_date": 0.0,
            "total_withdrawal": 0.0,
            "lot_multiplier": 1.0,
            "copy_settings": {},
            "joined_at": datetime.now(),
            "approved_at": None,
            "approved_by": None
        }

        # Insert membership
        member_result = await db.members.insert_one(member_doc)

        return APIResponse(
            success=True,
            message="Join request submitted successfully",
            data={
                "member_id": str(member_result.inserted_id),
                "account_id": account_id,
                "status": "pending"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining group: {str(e)}")


@router.post("/leave", response_model=APIResponse)
async def leave_current_group(current_user_id: str = Depends(get_current_user)):
    """Leave current group"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Check if user is in a group
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user or not user.get("group_id"):
            raise HTTPException(status_code=400, detail="You are not currently in any group")

        # Update user record to remove group membership
        await db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$unset": {
                "group_id": "",
                "group_join_date": "",
                "referral_code_used": ""
            },
            "$set": {
                "updated_at": datetime.now()
            }}
        )

        return APIResponse(
            success=True,
            message="Successfully left the group",
            data={"left_at": datetime.now().isoformat()}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leaving group: {str(e)}")


@router.get("/{group_id}/referral-info", response_model=APIResponse)
async def get_group_referral_info(
    group_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Get referral code and API key for a group (masters only)"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Check if user is master of this group or admin
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        group = await db.groups.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Check permissions (group creator/master or admin)
        if user.get("role") != "admin" and group.get("created_by") != current_user_id:
            raise HTTPException(status_code=403, detail="Only group masters can access referral information")

        return APIResponse(
            success=True,
            message="Referral information retrieved successfully",
            data={
                "group_id": group_id,
                "group_name": group["group_name"],
                "referral_code": group.get("referral_code"),
                "api_key": group.get("api_key"),
                "referral_link": f"/groups/join?ref={group.get('referral_code')}",
                "total_members": await db.users.count_documents({"group_id": group_id})
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting referral info: {str(e)}")


@router.post("/{group_id}/leave", response_model=APIResponse)
async def leave_group(
    group_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Leave a trading group"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Find membership
        member = await db.members.find_one({
            "user_id": current_user_id,
            "group_id": group_id
        })

        if not member:
            raise HTTPException(status_code=404, detail="Not a member of this group")

        # Update member status to left
        await db.members.update_one(
            {"_id": member["_id"]},
            {"$set": {"status": "left", "left_at": datetime.now()}}
        )

        # Update trading account status
        if member.get("account_id"):
            await db.trading_accounts.update_one(
                {"_id": ObjectId(member["account_id"])},
                {"$set": {"status": "inactive", "updated_at": datetime.now()}}
            )

        return APIResponse(
            success=True,
            message="Successfully left the group"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leaving group: {str(e)}")

@router.get("/{group_id}/members", response_model=APIResponse)
async def get_group_members(
    group_id: str,
    current_user = Depends(verify_admin_or_manager)
):
    """Get all members of a group"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get members with user details
        pipeline = [
            {"$match": {"group_id": group_id}},
            {
                "$lookup": {
                    "from": "users",
                    "let": {"user_id": {"$toObjectId": "$user_id"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}}],
                    "as": "user"
                }
            },
            {"$unwind": "$user"},
            {
                "$lookup": {
                    "from": "trading_accounts",
                    "let": {"account_id": {"$toObjectId": "$account_id"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$account_id"]}}}],
                    "as": "account"
                }
            },
            {"$unwind": {"path": "$account", "preserveNullAndEmptyArrays": True}}
        ]

        members_cursor = db.members.aggregate(pipeline)
        members = await members_cursor.to_list(length=None)

        formatted_members = []
        for member in members:
            formatted_members.append({
                "member_id": str(member["_id"]),
                "user_id": str(member["user_id"]),
                "user_name": member["user"]["name"],
                "user_email": member["user"]["email"],
                "user_mobile": member["user"]["mobile"],
                "status": member["status"],
                "account_number": member.get("account", {}).get("account_number"),
                "broker": member.get("account", {}).get("broker"),
                "current_balance": member.get("current_balance", 0.0),
                "profit_till_date": member.get("profit_till_date", 0.0),
                "joined_at": member["joined_at"].isoformat() if member.get("joined_at") else None
            })

        return APIResponse(
            success=True,
            message="Group members retrieved successfully",
            data={"members": formatted_members, "total": len(formatted_members)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving group members: {str(e)}")

@router.patch("/members/{member_id}/approve", response_model=APIResponse)
async def approve_member(
    member_id: str,
    current_user = Depends(verify_admin_or_manager)
):
    """Approve a group member"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Update member status
        result = await db.members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": {
                "status": "active",
                "approved_at": datetime.now(),
                "approved_by": str(current_user["_id"])
            }}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Member not found")

        # Also approve the trading account
        member = await db.members.find_one({"_id": ObjectId(member_id)})
        if member and member.get("account_id"):
            await db.trading_accounts.update_one(
                {"_id": ObjectId(member["account_id"])},
                {"$set": {"status": "approved", "updated_at": datetime.now()}}
            )

        return APIResponse(
            success=True,
            message="Member approved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving member: {str(e)}")

@router.patch("/members/{member_id}/reject", response_model=APIResponse)
async def reject_member(
    member_id: str,
    rejection_data: dict,
    current_user = Depends(verify_admin_or_manager)
):
    """Reject a group member"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        reason = rejection_data.get("reason", "No reason provided")

        # Update member status
        result = await db.members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": {
                "status": "rejected",
                "rejected_at": datetime.now(),
                "rejected_by": str(current_user["_id"]),
                "rejection_reason": reason
            }}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Member not found")

        # Also reject the trading account
        member = await db.members.find_one({"_id": ObjectId(member_id)})
        if member and member.get("account_id"):
            await db.trading_accounts.update_one(
                {"_id": ObjectId(member["account_id"])},
                {"$set": {"status": "rejected", "updated_at": datetime.now()}}
            )

        return APIResponse(
            success=True,
            message="Member rejected successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting member: {str(e)}")

@router.get("/pending-members", response_model=APIResponse)
async def get_pending_members(
    current_user = Depends(verify_admin_or_manager)
):
    """Get all pending members across all groups"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get pending members with user and group details
        pipeline = [
            {"$match": {"status": "pending"}},
            {
                "$lookup": {
                    "from": "users",
                    "let": {"user_id": {"$toObjectId": "$user_id"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}}],
                    "as": "user"
                }
            },
            {"$unwind": "$user"},
            {
                "$lookup": {
                    "from": "groups",
                    "let": {"group_id": {"$toObjectId": "$group_id"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$group_id"]}}}],
                    "as": "group"
                }
            },
            {"$unwind": "$group"},
            {
                "$lookup": {
                    "from": "trading_accounts",
                    "let": {"account_id": {"$toObjectId": "$account_id"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$account_id"]}}}],
                    "as": "account"
                }
            },
            {"$unwind": {"path": "$account", "preserveNullAndEmptyArrays": True}}
        ]

        members_cursor = db.members.aggregate(pipeline)
        members = await members_cursor.to_list(length=None)

        formatted_members = []
        for member in members:
            formatted_members.append({
                "member_id": str(member["_id"]),
                "user_id": str(member["user_id"]),
                "user_name": member["user"]["name"],
                "user_email": member["user"]["email"],
                "user_mobile": member["user"]["mobile"],
                "group_name": member["group"]["group_name"],
                "group_id": str(member["group"]["_id"]),
                "status": member["status"],
                "account_number": member.get("account", {}).get("account_number"),
                "account_type": member.get("account", {}).get("account_type"),
                "broker": member.get("account", {}).get("broker"),
                "balance": member.get("account", {}).get("balance", 0.0),
                "current_balance": member.get("current_balance", 0.0),
                "profit_till_date": member.get("profit_till_date", 0.0),
                "lot_multiplier": member.get("lot_multiplier", 1.0),
                "joined_at": member["joined_at"].isoformat() if member.get("joined_at") else None
            })

        return APIResponse(
            success=True,
            message="Pending members retrieved successfully",
            data={"members": formatted_members, "total": len(formatted_members)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pending members: {str(e)}")