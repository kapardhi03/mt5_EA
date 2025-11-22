# ===================================
# api/support.py - Support System
# ===================================
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from backend.models.common import APIResponse
from backend.services.support_service import support_service
from backend.core.security import get_current_user
from typing import Literal

router = APIRouter()

class SupportTicketCreate(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    priority: Literal["low", "medium", "high"] = "medium"
    category: Literal["account", "trading", "payment", "technical", "other"] = "other"

@router.post("/tickets", response_model=APIResponse)
async def create_support_ticket(
    ticket_data: SupportTicketCreate,
    current_user_id: str = Depends(get_current_user)
):
    """Create support ticket"""
    
    result = await support_service.create_ticket(ticket_data.dict(), current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message=result["message"],
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create support ticket"
        )

@router.get("/tickets", response_model=APIResponse)
async def get_user_tickets(current_user_id: str = Depends(get_current_user)):
    """Get user's support tickets"""
    
    result = await support_service.get_user_tickets(current_user_id)
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="Support tickets retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch support tickets"
        )

@router.get("/faqs", response_model=APIResponse)
async def get_faqs():
    """Get frequently asked questions"""
    
    result = await support_service.get_faqs()
    
    if result["status"]:
        return APIResponse(
            success=True,
            message="FAQs retrieved successfully",
            data=result["data"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch FAQs"
        )