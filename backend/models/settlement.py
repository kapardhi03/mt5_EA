# ===================================
# models/settlement.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class SettlementCreate(BaseModel):
    group_id: str = Field(..., min_length=1)
    period_from: datetime
    period_to: datetime
    payment_method: str = Field(..., min_length=1)
    payment_reference: str = Field(..., min_length=1)
    amount_paid: float = Field(..., gt=0)
    payment_proof_file: Optional[str] = None  # File path after upload

class SettlementApproval(BaseModel):
    admin_otp: str = Field(..., min_length=4, max_length=10)
    status: Literal["approved", "rejected"]
    remarks: Optional[str] = None

class SettlementResponse(BaseModel):
    settlement_id: str
    group_id: str
    group_name: str
    period_from: datetime
    period_to: datetime
    total_profit: float
    profit_share_percent: float
    amount_due: float
    amount_paid: float
    payment_method: str
    payment_reference: str
    status: str
    submitted_by: str
    approved_by: Optional[str]
    auto_paused: bool
    created_at: datetime
