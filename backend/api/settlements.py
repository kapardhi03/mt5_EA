# ===================================
# api/settlements.py (Complete Implementation)
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from backend.models.common import APIResponse
from backend.models.settlement import SettlementCreate, SettlementApproval, SettlementResponse
from backend.services.settlement_service import settlement_service
from backend.services.user_service import user_service
from backend.core.security import get_current_user
import os
import uuid

router = APIRouter()

@router.post("/calculate", response_model=APIResponse)
async def calculate_settlement(
    group_id: str,
    period_from: str,  # ISO format date
    period_to: str,    # ISO format date
    current_user_id: str = Depends(get_current_user)
):
    """Calculate profit sharing for a group"""
    
    from datetime import datetime
    
    try:
        period_from_dt = datetime.fromisoformat(period_from.replace('Z', '+00:00'))
        period_to_dt = datetime.fromisoformat(period_to.replace('Z', '+00:00'))
        
        result = await settlement_service.calculate_profit_sharing(
            group_id, period_from_dt, period_to_dt
        )
        
        if result["status"]:
            return APIResponse(
                success=True,
                message="Settlement calculated successfully",
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format"
        )

@router.post("/", response_model=APIResponse)
async def submit_settlement(
    settlement_data: SettlementCreate,
    current_user_id: str = Depends(get_current_user)
):
    """Submit settlement request"""
    
    result = await settlement_service.submit_settlement(
        settlement_data.dict(), current_user_id
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

@router.get("/pending", response_model=APIResponse)
async def get_pending_settlements(current_user_id: str = Depends(get_current_user)):
    """Get pending settlements (Admin only)"""
    
    # Verify admin access
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    result = await settlement_service.get_pending_settlements()
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Pending settlements retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

@router.put("/{settlement_id}/approve", response_model=APIResponse)
async def approve_settlement(
    settlement_id: str,
    approval_data: SettlementApproval,
    current_user_id: str = Depends(get_current_user)
):
    """Approve or reject settlement (Admin only with OTP)"""
    
    # Verify admin access
    user_result = await user_service.get_user_by_id(current_user_id)
    if not user_result["status"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user = user_result["data"]
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    result = await settlement_service.approve_settlement(
        settlement_id, approval_data.dict(), current_user_id
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

@router.post("/upload-proof", response_model=APIResponse)
async def upload_payment_proof(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user)
):
    """Upload payment proof file"""
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/settlement_proofs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return APIResponse(
            success=True,
            message="File uploaded successfully",
            data={"file_path": file_path, "filename": unique_filename}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
