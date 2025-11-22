# ===================================
# models/support.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

class SupportTicket(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    priority: Literal["low", "medium", "high"] = "medium"
    category: str = Field(..., min_length=1)

class TicketResponse(BaseModel):
    ticket_id: str
    subject: str
    message: str
    status: str
    priority: str
    category: str
    created_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    responses: List[dict]

class FAQ(BaseModel):
    question: str
    answer: str
    category: str
    order: int