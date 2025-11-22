# ===================================
# models/member.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class AllocationModel(BaseModel):
    type: Literal["fixed_lot", "ratio", "equity_proportional"] = "ratio"
    value: float = Field(..., gt=0)
    min_lot: Optional[float] = Field(0.01, gt=0)
    max_lot: Optional[float] = Field(100.0, gt=0)

class MemberCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    group_id: str = Field(..., min_length=1)
    broker: str = Field(..., min_length=1)
    server: str = Field(..., min_length=1)
    account_no: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    opening_balance: float = Field(..., gt=0)
    allocation_model: AllocationModel

class MemberAccountLink(BaseModel):
    broker: str = Field(..., min_length=1)
    server: str = Field(..., min_length=1)
    account_no: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    opening_balance: float = Field(..., gt=0)

class MemberUpdate(BaseModel):
    status: Optional[Literal["active", "paused", "inactive"]] = None
    allocation_model: Optional[AllocationModel] = None

class MemberResponse(BaseModel):
    member_id: str
    user_id: str
    group_id: str
    group_name: str
    user_name: str
    mobile: str
    email: str
    broker: str
    server: str
    account_no: str
    opening_balance: float
    opening_date: datetime
    copy_start_date: Optional[datetime]
    status: str
    last_sync: Optional[datetime]
    last_error: Optional[str]
    allocation_model: dict
    trade_copier_mapping: dict
    created_at: datetime