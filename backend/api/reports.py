# ===================================
# ENHANCED api/reports.py - Complete reporting system
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models.common import APIResponse, PaginationParams
from backend.services.user_service import user_service
from backend.services.member_service import member_service
from backend.services.group_service import group_service
from backend.services.settlement_service import settlement_service
from backend.core.security import get_current_user
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

async def verify_admin(current_user_id: str = Depends(get_current_user)):
    """Verify admin access"""
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return user

@router.get("/members", response_model=APIResponse)
async def get_member_reports(
    group_id: Optional[str] = Query(None, description="Filter by group"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user_id: str = Depends(get_current_user)
):
    """Get detailed member reports with filters"""
    
    try:
        # Get current user to check permissions
        user_result = await user_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = user_result["data"]
        
        # Build filter query
        filters = {}
        if group_id:
            filters["group_id"] = group_id
        if status:
            filters["status"] = status
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter["$lte"] = datetime.fromisoformat(date_to)
            filters["created_at"] = date_filter
        
        # Get members based on role
        if user["role"] == "admin":
            # Admin sees all members
            result = await member_service.get_members()
        elif user["role"] == "group_manager":
            # Group manager sees only their group members
            # TODO: Implement group ownership check
            result = await member_service.get_members(group_id=group_id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        if result["status"]:
            # Enrich with additional report data
            enriched_members = []
            for member in result["data"]:
                # Add calculated fields for report
                member["profit_percentage"] = 0.0
                if member["opening_balance"] > 0:
                    # Mock profit calculation (replace with actual)
                    member["profit_percentage"] = (member.get("profit_till_date", 0) / member["opening_balance"]) * 100
                
                member["account_no_masked"] = f"****{member['account_no'][-4:]}" if len(member["account_no"]) > 4 else "****"
                member["days_active"] = (datetime.utcnow() - member["created_at"]).days if isinstance(member["created_at"], datetime) else 0
                
                enriched_members.append(member)
            
            return APIResponse(
                success=True,
                message="Member reports retrieved successfully",
                data=enriched_members
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch member reports"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

@router.get("/groups", response_model=APIResponse)
async def get_group_reports(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user)
):
    """Get detailed group performance reports"""
    
    try:
        user_result = await user_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = user_result["data"]
        
        # Get groups based on role
        result = await group_service.get_groups(current_user_id, user["role"])
        
        if result["status"]:
            enriched_groups = []
            for group in result["data"]:
                # Calculate group metrics
                group_metrics = {
                    "group_id": group["group_id"],
                    "group_name": group["group_name"],
                    "company_name": group["company_name"],
                    "settlement_cycle": group["settlement_cycle"],
                    "total_members": group.get("total_members", 0),
                    "active_members": group.get("active_members", 0),
                    "profit_sharing_percent": group["profit_sharing_percent"],
                    "trading_status": group["trading_status"],
                    "created_at": group["created_at"],
                    "created_by": group["created_by"],
                    
                    # Mock calculated fields (replace with actual calculations)
                    "total_equity": 125000.0,
                    "total_profit_till_date": 15420.0,
                    "gross_profit_period": 3420.0,
                    "total_sharing_paid": 4626.0,
                    "pending_sharing_amount": 1026.0,
                    "last_settlement_date": "2025-09-10",
                    "next_due_date": "2025-10-10"
                }
                enriched_groups.append(group_metrics)
            
            return APIResponse(
                success=True,
                message="Group reports retrieved successfully",
                data=enriched_groups
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch group reports"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

@router.get("/settlements", response_model=APIResponse)
async def get_settlement_reports(
    group_id: Optional[str] = Query(None, description="Filter by group"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user)
):
    """Get settlement/payment reports"""
    
    try:
        user_result = await user_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = user_result["data"]
        
        # Mock settlement report data (replace with actual service call)
        settlement_reports = [
            {
                "sr_no": 1,
                "date_time": "2025-09-15T10:30:00Z",
                "group_name": "Alpha Trading Group",
                "settlement_period_from": "2025-09-01",
                "settlement_period_to": "2025-09-30",
                "profit_due": 3420.00,
                "amount_paid": 3420.00,
                "payment_method": "Bank Transfer",
                "reference_utr": "UTR123456789",
                "received_by": "John Admin",
                "approved_by": "Super Admin",
                "otp_id": "OTP789",
                "approval_time": "2025-09-15T11:00:00Z",
                "status": "approved",
                "auto_pause": False,
                "resume_time": None
            },
            {
                "sr_no": 2,
                "date_time": "2025-09-14T15:45:00Z",
                "group_name": "Beta Forex Group",
                "settlement_period_from": "2025-09-01",
                "settlement_period_to": "2025-09-30",
                "profit_due": 2150.50,
                "amount_paid": 2150.50,
                "payment_method": "UPI",
                "reference_utr": "UPI987654321",
                "received_by": "Jane Manager",
                "approved_by": None,
                "otp_id": None,
                "approval_time": None,
                "status": "pending",
                "auto_pause": False,
                "resume_time": None
            }
        ]
        
        # Apply filters (implement actual filtering logic)
        filtered_reports = settlement_reports
        if group_id:
            filtered_reports = [r for r in filtered_reports if group_id.lower() in r["group_name"].lower()]
        if status:
            filtered_reports = [r for r in filtered_reports if r["status"] == status]
        
        return APIResponse(
            success=True,
            message="Settlement reports retrieved successfully",
            data=filtered_reports
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

@router.get("/errors", response_model=APIResponse)
async def get_error_reports(
    member_id: Optional[str] = Query(None, description="Filter by member"),
    group_id: Optional[str] = Query(None, description="Filter by group"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    admin_user = Depends(verify_admin)
):
    """Get error/failure reports (Admin only)"""
    
    try:
        # Mock error report data (replace with actual service call)
        error_reports = [
            {
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
                "resolved_at": None
            },
            {
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
                "resolved_at": "2025-09-15T14:00:00Z"
            }
        ]
        
        # Apply filters
        filtered_errors = error_reports
        if member_id:
            filtered_errors = [e for e in filtered_errors if member_id in e["account_no"]]
        if group_id:
            filtered_errors = [e for e in filtered_errors if group_id.lower() in e["group"].lower()]
        if resolved is not None:
            filtered_errors = [e for e in filtered_errors if e["resolved"] == resolved]
        
        return APIResponse(
            success=True,
            message="Error reports retrieved successfully",
            data=filtered_errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch error reports"
        )

@router.get("/performance", response_model=APIResponse)
async def get_performance_reports(
    report_type: str = Query(..., description="Type: daily, weekly, monthly"),
    group_id: Optional[str] = Query(None, description="Filter by group"),
    member_id: Optional[str] = Query(None, description="Filter by member"),
    current_user_id: str = Depends(get_current_user)
):
    """Get performance reports (daily/weekly/monthly)"""
    
    try:
        user_result = await user_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = user_result["data"]
        
        # Mock performance data based on report type
        if report_type == "daily":
            performance_data = [
                {"date": "2025-09-15", "total_profit": 1245.50, "trades": 24, "win_rate": 65.0},
                {"date": "2025-09-14", "total_profit": 892.25, "trades": 18, "win_rate": 61.1},
                {"date": "2025-09-13", "total_profit": 1567.75, "trades": 31, "win_rate": 71.0}
            ]
        elif report_type == "weekly":
            performance_data = [
                {"week": "2025-W37", "total_profit": 4250.50, "trades": 89, "win_rate": 66.2},
                {"week": "2025-W36", "total_profit": 3890.25, "trades": 76, "win_rate": 63.8}
            ]
        elif report_type == "monthly":
            performance_data = [
                {"month": "2025-09", "total_profit": 15420.75, "trades": 342, "win_rate": 65.5},
                {"month": "2025-08", "total_profit": 12890.50, "trades": 298, "win_rate": 62.1}
            ]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report type")
        
        return APIResponse(
            success=True,
            message=f"{report_type.title()} performance reports retrieved successfully",
            data=performance_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch performance reports"
        )

@router.get("/export", response_model=APIResponse)
async def export_reports(
    report_type: str = Query(..., description="members, groups, settlements, errors"),
    format: str = Query("csv", description="Export format: csv, excel"),
    group_id: Optional[str] = Query(None, description="Filter by group"),
    date_from: Optional[str] = Query(None, description="Start date"),
    date_to: Optional[str] = Query(None, description="End date"),
    current_user_id: str = Depends(get_current_user)
):
    """Export reports to CSV/Excel"""
    
    try:
        user_result = await user_service.get_user_by_id(current_user_id)
        if not user_result["status"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = user_result["data"]
        if user["role"] not in ["admin", "group_manager"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Generate export file (mock implementation)
        export_filename = f"{report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        # TODO: Implement actual export logic
        # - Query data based on filters
        # - Generate CSV/Excel file
        # - Store in temporary location
        # - Return download URL
        
        return APIResponse(
            success=True,
            message="Report export generated successfully",
            data={
                "filename": export_filename,
                "download_url": f"/downloads/{export_filename}",
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate export"
        )