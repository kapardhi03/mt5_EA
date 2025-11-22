# ===================================
# ENHANCED api/admin.py - Complete admin management system
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models.common import APIResponse
from backend.models.user import UserRegistration
from backend.services.user_service import user_service
from backend.services.group_service import group_service
from backend.services.member_service import member_service
from backend.services.settlement_service import settlement_service
from backend.core.security import get_current_user, hash_password
from backend.core.config import settings
from backend.utils.mongo import insert_document, fetch_documents, update_document
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

from backend.services.mongodb_service import mongodb_service
from backend.services.realtime_service import realtime_service

async def verify_admin(current_user_id: str = Depends(get_current_user)):
    """Verify that current user is admin"""
    user_result = await mongodb_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return user

@router.get("/dashboard", response_model=APIResponse)
async def admin_dashboard(admin_user = Depends(verify_admin)):
    """Enhanced admin dashboard with comprehensive metrics"""
    
    try:
        # Get comprehensive dashboard data
        users_result = fetch_documents(settings.DATABASE_NAME, "users", {"status": {"$ne": "deleted"}})
        groups_result = fetch_documents(settings.DATABASE_NAME, "groups", {"status": "active"})
        members_result = fetch_documents(settings.DATABASE_NAME, "members", {"status": {"$ne": "deleted"}})
        settlements_result = fetch_documents(settings.DATABASE_NAME, "settlements", {"status": "pending"})
        
        # Calculate active users
        active_users = len([u for u in users_result.get("data", []) if u.get("status") == "active"])
        
        # Mock trading metrics (replace with actual Trade Copier API calls)
        dashboard_data = {
            # User Statistics
            "total_users": len(users_result["data"]) if users_result["status"] else 0,
            "active_users": active_users,
            "pending_users": len([u for u in users_result.get("data", []) if u.get("status") == "pending"]),
            
            # Group Statistics  
            "total_groups": len(groups_result["data"]) if groups_result["status"] else 0,
            "active_groups": len([g for g in groups_result.get("data", []) if g.get("trading_status") == "active"]),
            
            # Member Statistics
            "total_members": len(members_result["data"]) if members_result["status"] else 0,
            "active_members": len([m for m in members_result.get("data", []) if m.get("status") == "active"]),
            
            # Trading Metrics (Mock - replace with actual data)
            "total_equity": 525000.0,
            "total_profit": 45420.50,
            "today_profit": 2340.25,
            "running_trades": 42,
            "master_accounts": 4,
            
            # Settlement Statistics
            "pending_settlements_count": len(settlements_result["data"]) if settlements_result["status"] else 0,
            "pending_settlements_amount": 15420.50,  # Mock
            
            # Error Statistics (Mock)
            "active_errors": 3,
            "resolved_errors_today": 7,
            
            # Admin Info
            "admin_user": admin_user["name"],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return APIResponse(
            success=True,
            message="Admin dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/users", response_model=APIResponse)
async def list_all_users(
    status: Optional[str] = Query(None, description="Filter by status"),
    role: Optional[str] = Query(None, description="Filter by role"),
    search: Optional[str] = Query(None, description="Search by name, email, or mobile"),
    admin_user = Depends(verify_admin)
):
    """Enhanced user list with filters and search"""
    
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        if role:
            query["role"] = role
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"mobile": {"$regex": search, "$options": "i"}}
            ]
        
        result = fetch_documents(
            settings.DATABASE_NAME,
            "users",
            query,
            sort=[("created_at", -1)]
        )
        
        if result["status"]:
            # Clean user data and add additional info
            enhanced_users = []
            for user in result["data"]:
                clean_user = user_service.clean_user_data(user)
                
                # Add member count for this user
                member_count = fetch_documents(
                    settings.DATABASE_NAME,
                    "members", 
                    {"user_id": user["user_id"], "status": {"$ne": "deleted"}}
                )
                clean_user["linked_accounts"] = len(member_count["data"]) if member_count["status"] else 0
                clean_user["account_no_masked"] = f"****{user.get('mobile', '')[-4:]}" if user.get('mobile') else "****"
                
                enhanced_users.append(clean_user)
            
            return APIResponse(
                success=True,
                message="Users retrieved successfully",
                data=enhanced_users
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

@router.post("/users/create-admin", response_model=APIResponse)
async def create_admin_user(user_data: UserRegistration, admin_user = Depends(verify_admin)):
    """Create a new admin user"""
    
    # Check if user already exists
    existing_user = fetch_documents(
        settings.DATABASE_NAME, 
        "users", 
        {"$or": [{"email": user_data.email}, {"mobile": user_data.mobile}]}
    )
    
    if existing_user["status"] and existing_user["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or mobile already exists"
        )
    
    # Create admin user record
    admin_record = {
        "user_id": str(uuid.uuid4()),
        "name": user_data.name,
        "mobile": user_data.mobile,
        "email": user_data.email,
        "country": user_data.country,
        "state": user_data.state,
        "city": user_data.city,
        "pin_code": user_data.pin_code,
        "password": hash_password(user_data.password),
        "role": "admin",  # Set as admin
        "status": "active",  # Auto-activate admin users
        "mobile_verified": True,
        "email_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": admin_user["user_id"]
    }
    
    # Insert admin user
    result = insert_document(settings.DATABASE_NAME, "users", admin_record)
    
    if result["status"]:
        clean_admin = user_service.clean_user_data(admin_record)
        return APIResponse(
            success=True,
            message="Admin user created successfully",
            data=clean_admin
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin user"
        )

@router.put("/users/{user_id}/role", response_model=APIResponse)
async def update_user_role(
    user_id: str,
    new_role: str,
    admin_user = Depends(verify_admin)
):
    """Update user role (admin, group_manager, member)"""
    
    valid_roles = ["admin", "group_manager", "member"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(valid_roles)}"
        )
    
    # Update user role
    result = update_document(
        settings.DATABASE_NAME,
        "users",
        "user_id",
        user_id,
        {"role": new_role}
    )
    
    if result["status"]:
        # Get updated user
        updated_user = await user_service.get_user_by_id(user_id)
        return APIResponse(
            success=True,
            message=f"User role updated to {new_role}",
            data=updated_user["data"] if updated_user["status"] else None
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )

@router.put("/users/{user_id}/status", response_model=APIResponse)
async def update_user_status(
    user_id: str,
    new_status: str,
    admin_user = Depends(verify_admin)
):
    """Update user status (active, pending, inactive)"""
    
    valid_statuses = ["active", "pending", "inactive"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update user status
    result = update_document(
        settings.DATABASE_NAME,
        "users",
        "user_id",
        user_id,
        {"status": new_status}
    )
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=f"User status updated to {new_status}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )

# ===== IB PROOF MANAGEMENT =====

@router.get("/ib-proofs/pending", response_model=APIResponse)
async def get_pending_ib_proofs(admin_user = Depends(verify_admin)):
    """Get all users with pending IB proof approvals"""
    try:
        db = mongodb_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Find users with pending IB status.
        # Accept both the correct value 'pending' and a possible misspelling 'plending'
        # so admins can review and approve those users too.
        pending_users = await db.users.find({
            "ib_status": {"$in": ["pending", "plending"]}
        }).to_list(length=None)

        # Format the data for admin review
        formatted_users = []
        for user in pending_users:
            formatted_users.append({
                "user_id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "mobile": user.get("mobile"),
                "country": user.get("country"),
                "state": user.get("state"),
                "city": user.get("city"),
                "pin_code": user.get("pin_code"),
                "role": user.get("role"),
                "mobile_verified": user.get("mobile_verified", False),
                "email_verified": user.get("email_verified", False),
                "broker": user.get("broker"),
                "account_no": user.get("account_no"),
                "ib_proof_filename": user.get("ib_proof_filename"),
                "ib_proof_upload_date": user.get("ib_proof_upload_date"),
                "ib_proof_image_data": user.get("ib_proof_image_data"),
                "ib_status": user.get("ib_status"),
                "status": user.get("status"),
                "created_at": user.get("created_at")
            })

        return APIResponse(
            success=True,
            message=f"Found {len(formatted_users)} pending IB proofs",
            data={"pending_proofs": formatted_users}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ib-proofs/approve", response_model=APIResponse)
async def approve_ib_proof(
    user_id: str = Query(..., description="User ID to approve"),
    admin_user = Depends(verify_admin)
):
    """Approve a user's IB proof"""
    try:
        db = mongodb_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")

        from bson import ObjectId

        # Update user record
        print(f"🔄 Updating user {user_id} with IB approval...")
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "ib_status": "approved",
                "ib_approval_date": datetime.now(),
                "ib_approved_by": admin_user["name"],
                "status": "active",
                "updated_at": datetime.now()
            }}
        )

        print(f"📊 Database update result: modified_count={result.modified_count}, matched_count={result.matched_count}")

        if result.modified_count == 0:
            # Check if user exists but wasn't modified (already processed)
            user_exists = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user_exists:
                raise HTTPException(status_code=404, detail="User not found")
            else:
                print(f"⚠️ User {user_id} exists but wasn't modified (may already be processed)")
                # Still return success but with a warning
                return APIResponse(
                    success=True,
                    message="User already processed or no changes needed",
                    data={"user_id": user_id, "status": "already_processed"}
                )

        # Get user details for notification
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        user_name = user.get("name", "Unknown") if user else "Unknown"

        # Send real-time notification to user (if service available)
        try:
            await realtime_service.notify_user(
                user_id,
                "ib_approved",
                {
                    "message": "Your IB proof has been approved! EA features are now enabled.",
                    "status": "approved",
                    "approved_by": admin_user["name"],
                    "approved_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Realtime notification failed: {e}")

        # Send real-time notification to all admins (if service available)
        try:
            await realtime_service.notify_admins(
                "ib_proof_processed",
                {
                    "action": "approved",
                    "user_id": user_id,
                    "user_name": user_name,
                    "approved_by": admin_user["name"],
                    "processed_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Admin notification failed: {e}")

        return APIResponse(
            success=True,
            message="IB proof approved successfully",
            data={"user_id": user_id, "status": "approved"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ib-proofs/reject", response_model=APIResponse)
async def reject_ib_proof(
    user_id: str = Query(..., description="User ID to reject"),
    rejection_reason: str = Query(..., description="Reason for rejection"),
    admin_user = Depends(verify_admin)
):
    """Reject a user's IB proof"""
    try:
        db = mongodb_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")

        from bson import ObjectId

        # Update user record
        print(f"🔄 Updating user {user_id} with IB rejection...")
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "ib_status": "rejected",
                "ib_rejection_reason": rejection_reason,
                "ib_approved_by": admin_user["name"],
                "status": "pending_ib_change",  # Keep them in pending state to retry
                "updated_at": datetime.now()
            }}
        )

        print(f"📊 Database update result: modified_count={result.modified_count}, matched_count={result.matched_count}")

        if result.modified_count == 0:
            # Check if user exists but wasn't modified (already processed)
            user_exists = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user_exists:
                raise HTTPException(status_code=404, detail="User not found")
            else:
                print(f"⚠️ User {user_id} exists but wasn't modified (may already be processed)")
                # Still return success but with a warning
                return APIResponse(
                    success=True,
                    message="User already processed or no changes needed",
                    data={"user_id": user_id, "status": "already_processed"}
                )

        # Get user details for notification
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        user_name = user.get("name", "Unknown") if user else "Unknown"

        # Send real-time notification to user (if service available)
        try:
            await realtime_service.notify_user(
                user_id,
                "ib_rejected",
                {
                    "message": f"Your IB proof was rejected: {rejection_reason}",
                    "status": "rejected",
                    "rejection_reason": rejection_reason,
                    "rejected_by": admin_user["name"],
                    "rejected_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Realtime notification failed: {e}")

        # Send real-time notification to all admins (if service available)
        try:
            await realtime_service.notify_admins(
                "ib_proof_processed",
                {
                    "action": "rejected",
                    "user_id": user_id,
                    "user_name": user_name,
                    "rejection_reason": rejection_reason,
                    "rejected_by": admin_user["name"],
                    "processed_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Admin notification failed: {e}")

        return APIResponse(
            success=True,
            message="IB proof rejected successfully",
            data={"user_id": user_id, "status": "rejected", "reason": rejection_reason}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ib-proofs/verify/{user_id}", response_model=APIResponse)
async def verify_ib_proof_status(
    user_id: str,
    admin_user = Depends(verify_admin)
):
    """Verify the current IB proof status of a user"""
    try:
        db = mongodb_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")

        from bson import ObjectId

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return APIResponse(
            success=True,
            message="User IB status retrieved successfully",
            data={
                "user_id": user_id,
                "name": user.get("name"),
                "email": user.get("email"),
                "ib_status": user.get("ib_status"),
                "status": user.get("status"),
                "ib_approval_date": user.get("ib_approval_date"),
                "ib_approved_by": user.get("ib_approved_by"),
                "ib_rejection_reason": user.get("ib_rejection_reason"),
                "updated_at": user.get("updated_at")
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== NEW ADMIN ENDPOINTS FOR COMPREHENSIVE MANAGEMENT =====

@router.get("/groups", response_model=APIResponse)
async def admin_get_all_groups(
    status: Optional[str] = Query(None, description="Filter by status"),
    trading_status: Optional[str] = Query(None, description="Filter by trading status"),
    admin_user = Depends(verify_admin)
):
    """Get all groups for admin management"""
    
    try:
        query = {}
        if status:
            query["status"] = status
        if trading_status:
            query["trading_status"] = trading_status
        
        result = await group_service.get_groups("admin_override", "admin")
        
        if result["status"]:
            return APIResponse(
                success=True,
                message="Groups retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch groups"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching groups: {str(e)}"
        )

@router.put("/groups/{group_id}/status", response_model=APIResponse)
async def admin_update_group_status(
    group_id: str,
    new_status: str,
    admin_user = Depends(verify_admin)
):
    """Enable/disable group (admin override)"""
    
    valid_statuses = ["active", "inactive", "suspended", "deleted"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    result = await group_service.update_group(group_id, {"status": new_status}, admin_user["user_id"])
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=f"Group status updated to {new_status}",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update group status"
        )

@router.get("/members", response_model=APIResponse)
async def admin_get_all_members(
    group_id: Optional[str] = Query(None, description="Filter by group"),
    status: Optional[str] = Query(None, description="Filter by status"),
    broker: Optional[str] = Query(None, description="Filter by broker"),
    search: Optional[str] = Query(None, description="Search by name/email/account"),
    admin_user = Depends(verify_admin)
):
    """Get all members for admin management with enhanced filters"""
    
    try:
        result = await member_service.get_members(group_id=group_id)
        
        if result["status"]:
            members = result["data"]
            
            # Apply additional filters
            if status:
                members = [m for m in members if m.get("status") == status]
            if broker:
                members = [m for m in members if broker.lower() in m.get("broker", "").lower()]
            if search:
                search_lower = search.lower()
                members = [m for m in members if 
                    search_lower in m.get("user_name", "").lower() or
                    search_lower in m.get("email", "").lower() or
                    search_lower in m.get("account_no", "").lower()
                ]
            
            # Add additional admin-specific data
            enhanced_members = []
            for member in members:
                # Add performance metrics (mock data)
                member["profit_percentage"] = 0.0
                if member.get("opening_balance", 0) > 0:
                    member["profit_percentage"] = (member.get("profit_till_date", 0) / member["opening_balance"]) * 100
                
                member["days_active"] = (datetime.utcnow() - member.get("created_at", datetime.utcnow())).days
                member["last_trade_sync"] = member.get("trade_copier_mapping", {}).get("last_trade_sync")
                
                enhanced_members.append(member)
            
            return APIResponse(
                success=True,
                message="Members retrieved successfully",
                data=enhanced_members
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch members"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching members: {str(e)}"
        )

@router.put("/members/{member_id}/approve", response_model=APIResponse)
async def admin_approve_member(
    member_id: str,
    action: str,  # "approve" or "reject"
    remarks: Optional[str] = None,
    admin_user = Depends(verify_admin)
):
    """Approve or reject member (admin action)"""
    
    if action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'approve' or 'reject'"
        )
    
    try:
        update_data = {
            "status": "active" if action == "approve" else "rejected",
            "approved_by": admin_user["user_id"],
            "approved_at": datetime.utcnow(),
            "approval_remarks": remarks
        }
        
        result = await member_service.update_member(member_id, update_data, admin_user["user_id"])
        
        if result["status"]:
            return APIResponse(
                success=True,
                message=f"Member {action}d successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to {action} member"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing member approval: {str(e)}"
        )

@router.get("/settlements/all", response_model=APIResponse)
async def admin_get_all_settlements(
    status: Optional[str] = Query(None, description="Filter by status"),
    group_id: Optional[str] = Query(None, description="Filter by group"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    admin_user = Depends(verify_admin)
):
    """Get all settlements for admin review"""
    
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        if group_id:
            query["group_id"] = group_id
        
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            query["submitted_at"] = date_filter
        
        result = fetch_documents(
            settings.DATABASE_NAME,
            "settlements",
            query,
            sort=[("submitted_at", -1)]
        )
        
        if result["status"]:
            # Enrich with group names
            enriched_settlements = []
            for settlement in result["data"]:
                group_result = await group_service.get_group_by_id(settlement["group_id"])
                if group_result["status"]:
                    settlement["group_name"] = group_result["data"]["group_name"]
                    settlement["company_name"] = group_result["data"]["company_name"]
                
                # Add user name who submitted
                user_result = await user_service.get_user_by_id(settlement["submitted_by"])
                if user_result["status"]:
                    settlement["submitted_by_name"] = user_result["data"]["name"]
                
                enriched_settlements.append(settlement)
            
            return APIResponse(
                success=True,
                message="Settlements retrieved successfully",
                data=enriched_settlements
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch settlements"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settlements: {str(e)}"
        )

@router.get("/error-logs", response_model=APIResponse)
async def admin_get_error_logs(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    member_id: Optional[str] = Query(None, description="Filter by member"),
    group_id: Optional[str] = Query(None, description="Filter by group"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(50, description="Number of records to fetch"),
    admin_user = Depends(verify_admin)
):
    """Get error logs for system monitoring (Admin only)"""
    
    try:
        # Mock error logs data (replace with actual error tracking service)
        error_logs = [
            {
                "error_id": "ERR001",
                "timestamp": "2025-09-15T14:30:15Z",
                "member_name": "John Trader",
                "account_no": "12345678",
                "group": "Alpha Trading",
                "master_account": "MASTER001",
                "symbol": "EURUSD",
                "trade_side": "buy",
                "volume_attempted": 1.0,
                "reason_code": "INSUFFICIENT_MARGIN",
                "reason_detail": "Not enough margin to open position",
                "server_response_code": "10019",
                "retry_count": 3,
                "resolved": False,
                "resolved_by": None,
                "resolved_at": None,
                "severity": "high"
            },
            {
                "error_id": "ERR002",
                "timestamp": "2025-09-15T13:15:22Z",
                "member_name": "Jane Smith",
                "account_no": "87654321",
                "group": "Beta Forex",
                "master_account": "MASTER002",
                "symbol": "GBPUSD",
                "trade_side": "sell",
                "volume_attempted": 0.5,
                "reason_code": "SYMBOL_DISABLED",
                "reason_detail": "Symbol trading is disabled",
                "server_response_code": "10041",
                "retry_count": 1,
                "resolved": True,
                "resolved_by": "Admin User",
                "resolved_at": "2025-09-15T14:00:00Z",
                "severity": "medium"
            }
        ]
        
        # Apply filters
        filtered_errors = error_logs
        if resolved is not None:
            filtered_errors = [e for e in filtered_errors if e["resolved"] == resolved]
        if member_id:
            filtered_errors = [e for e in filtered_errors if member_id in e["account_no"]]
        if group_id:
            filtered_errors = [e for e in filtered_errors if group_id.lower() in e["group"].lower()]
        
        # Apply limit
        filtered_errors = filtered_errors[:limit]
        
        return APIResponse(
            success=True,
            message="Error logs retrieved successfully",
            data=filtered_errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching error logs: {str(e)}"
        )

@router.put("/error-logs/{error_id}/resolve", response_model=APIResponse)
async def admin_resolve_error(
    error_id: str,
    resolution_notes: Optional[str] = None,
    admin_user = Depends(verify_admin)
):
    """Mark error as resolved (Admin action)"""
    
    try:
        # TODO: Update actual error tracking system
        # For now, return success response
        
        return APIResponse(
            success=True,
            message="Error marked as resolved successfully",
            data={
                "error_id": error_id,
                "resolved_by": admin_user["name"],
                "resolved_at": datetime.utcnow().isoformat(),
                "resolution_notes": resolution_notes
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving error log: {str(e)}"
        )

@router.get("/system-stats", response_model=APIResponse)
async def admin_get_system_stats(admin_user = Depends(verify_admin)):
    """Get comprehensive system statistics for admin"""
    
    try:
        # Mock system statistics (replace with actual system monitoring)
        system_stats = {
            "database": {
                "status": "healthy",
                "connections": 25,
                "response_time_ms": 45,
                "total_collections": 8,
                "total_documents": 1250
            },
            "trade_copier": {
                "status": "connected",
                "master_connections": 4,
                "slave_connections": 35,
                "avg_latency_ms": 120,
                "last_sync": "2025-09-15T14:30:00Z"
            },
            "api_performance": {
                "requests_per_minute": 150,
                "avg_response_time_ms": 85,
                "error_rate_percent": 0.2,
                "uptime_percent": 99.9
            },
            "server": {
                "cpu_usage_percent": 35,
                "memory_usage_percent": 65,
                "disk_usage_percent": 42,
                "active_connections": 128
            }
        }
        
        return APIResponse(
            success=True,
            message="System statistics retrieved successfully",
            data=system_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching system stats: {str(e)}"
        )

@router.post("/bootstrap", response_model=APIResponse)
async def bootstrap_admin():
    """Create initial admin user - only works if no admin exists"""
    
    # Check if any admin already exists
    existing_admin = fetch_documents(
        settings.DATABASE_NAME,
        "users",
        {"role": "admin"}
    )
    
    if existing_admin["status"] and existing_admin["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists. Use regular admin creation endpoint."
        )
    
    # Create bootstrap admin
    bootstrap_admin = {
        "user_id": str(uuid.uuid4()),
        "name": "Bootstrap Admin",
        "mobile": "+1000000000",
        "email": "admin@system.local",
        "country": "System",
        "state": "System",
        "city": "System",
        "pin_code": "00000",
        "password": hash_password("BootstrapAdmin123!"),
        "role": "admin",
        "status": "active",
        "mobile_verified": True,
        "email_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": "system"
    }
    
    result = insert_document(settings.DATABASE_NAME, "users", bootstrap_admin)
    
    if result["status"]:
        clean_admin = user_service.clean_user_data(bootstrap_admin)
        return APIResponse(
            success=True,
            message="Bootstrap admin created successfully",
            data={
                "admin": clean_admin,
                "login_credentials": {
                    "email": "admin@system.local",
                    "password": "BootstrapAdmin123!"
                }
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bootstrap admin"
        )

@router.patch("/users/activate", response_model=APIResponse)
async def activate_user(
    user_data: dict,
    admin_user = Depends(verify_admin)
):
    """Activate a user by email"""
    try:
        email = user_data.get("email")
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

@router.get("/pending-members", response_model=APIResponse)
async def get_pending_members(admin_user = Depends(verify_admin)):
    """Get all pending member approvals"""
    try:
        result = await mongodb_service.get_pending_members()

        if result["status"]:
            return APIResponse(
                success=True,
                message="Pending members retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-member/{member_id}", response_model=APIResponse)
async def approve_member(
    member_id: str,
    admin_user = Depends(verify_admin)
):
    """Approve a pending member"""
    try:
        result = await mongodb_service.approve_member(member_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reject-member/{member_id}", response_model=APIResponse)
async def reject_member(
    member_id: str,
    reason_data: dict,
    admin_user = Depends(verify_admin)
):
    """Reject a pending member"""
    try:
        result = await mongodb_service.reject_member(member_id, reason_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin-groups", response_model=APIResponse)
async def get_admin_groups(admin_user = Depends(verify_admin)):
    """Get all groups for admin management"""
    try:
        result = await mongodb_service.get_groups()

        if result["status"]:
            return APIResponse(
                success=True,
                message="Groups retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update-group-status/{group_id}", response_model=APIResponse)
async def update_group_status(
    group_id: str,
    status_data: dict,
    admin_user = Depends(verify_admin)
):
    """Update group status"""
    try:
        result = await mongodb_service.update_group_status(group_id, status_data)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================================
# COPY TRADING ADMIN ENDPOINTS
# ===================================

@router.get("/dashboard-data", response_model=APIResponse)
async def get_admin_dashboard_data(admin_user = Depends(verify_admin)):
    """Get comprehensive dashboard data for admin"""
    try:
        result = await mongodb_service.get_admin_dashboard_data()

        if result["status"]:
            return APIResponse(
                success=True,
                message="Admin dashboard data retrieved successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-accounts", response_model=APIResponse)
async def get_all_trading_accounts(admin_user = Depends(verify_admin)):
    """Get all trading accounts for admin review"""
    try:
        db = mongodb_service.get_db()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")

        # Get all trading accounts with user details
        accounts_cursor = db.trading_accounts.find({}).sort("created_at", -1)
        accounts = await accounts_cursor.to_list(length=None)

        detailed_accounts = []
        for account in accounts:
            user_result = await mongodb_service.get_user_by_id(account["user_id"])
            if user_result["status"]:
                user = user_result["data"]

                # Get group info if assigned
                group_info = None
                if account.get("group_id"):
                    from bson import ObjectId
                    group = await db.trading_groups.find_one({"_id": ObjectId(account["group_id"])})
                    if group:
                        group_info = {
                            "group_name": group["group_name"],
                            "company_name": group["company_name"]
                        }

                account_data = {
                    "account_id": str(account["_id"]),
                    "user_name": user["name"],
                    "user_email": user["email"],
                    "user_mobile": user["mobile"],
                    "broker": account["broker"],
                    "server": account["server"],
                    "account_number_masked": "*" * (len(account["account_number"]) - 4) + account["account_number"][-4:],
                    "account_type": account.get("account_type"),
                    "leverage": account.get("leverage"),
                    "currency": account.get("currency"),
                    "opening_balance": account.get("opening_balance", 0),
                    "current_balance": account.get("current_balance", 0),
                    "equity": account.get("equity", 0),
                    "profit_since_copy_start": account.get("profit_since_copy_start", 0),
                    "copy_status": account.get("copy_status"),
                    "copy_start_date": account.get("copy_start_date"),
                    "group_info": group_info,
                    "status": account.get("status"),
                    "ib_change_status": account.get("ib_change_status"),
                    "last_sync": account.get("last_sync"),
                    "last_error": account.get("last_error"),
                    "created_at": account["created_at"]
                }
                detailed_accounts.append(account_data)

        return APIResponse(
            success=True,
            message="Trading accounts retrieved successfully",
            data={"accounts": detailed_accounts}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/trading-accounts/{account_id}/status", response_model=APIResponse)
async def update_trading_account_status(
    account_id: str,
    status_data: dict,
    admin_user = Depends(verify_admin)
):
    """Update trading account status and assign to group"""
    try:
        status = status_data.get("status")
        group_id = status_data.get("group_id")

        result = await mongodb_service.update_account_status(account_id, status, group_id)

        if result["status"]:
            return APIResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-groups-admin", response_model=APIResponse)
async def get_all_trading_groups_admin(admin_user = Depends(verify_admin)):
    """Get all trading groups with detailed info for admin"""
    try:
        result = await mongodb_service.get_trading_groups()

        if result["status"]:
            groups = result["data"]["groups"]

            # Add detailed info for each group
            for group in groups:
                db = mongodb_service.get_db()
                if db:
                    # Get group leader info
                    leader_result = await mongodb_service.get_user_by_id(group["group_leader_id"])
                    if leader_result["status"]:
                        group["group_leader_name"] = leader_result["data"]["name"]
                        group["group_leader_email"] = leader_result["data"]["email"]

                    # Get member count
                    member_count = await db.trading_accounts.count_documents({
                        "group_id": group["id"],
                        "status": "approved"
                    })
                    group["actual_member_count"] = member_count

            return APIResponse(
                success=True,
                message="Trading groups retrieved successfully",
                data={"groups": groups}
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading-groups-create", response_model=APIResponse)
async def create_trading_group_admin(
    group_data: dict,
    admin_user = Depends(verify_admin)
):
    """Create a new trading group"""
    try:
        group_data["created_by"] = admin_user["id"]

        result = await mongodb_service.create_trading_group(group_data)

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