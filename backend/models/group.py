# ===================================
# models/group.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class MasterAccount(BaseModel):
    account_no: str = Field(..., min_length=1)
    broker: str = Field(..., min_length=1)
    server: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    investor_password: Optional[str] = None
    account_type: Literal["netting", "hedging"] = "netting"
    status: Literal["active", "inactive"] = "active"

class GroupCreate(BaseModel):
    group_name: str = Field(..., min_length=2, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=100)
    profit_sharing_percent: float = Field(..., ge=10, le=100)
    settlement_cycle: Literal["daily", "weekly", "monthly"]
    master_accounts: List[MasterAccount] = Field(..., min_items=1)

class GroupUpdate(BaseModel):
    group_name: Optional[str] = Field(None, min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    profit_sharing_percent: Optional[float] = Field(None, ge=10, le=100)
    settlement_cycle: Optional[Literal["daily", "weekly", "monthly"]] = None
    trading_status: Optional[Literal["active", "paused"]] = None

class GroupResponse(BaseModel):
    group_id: str
    group_name: str
    company_name: str
    profit_sharing_percent: float
    settlement_cycle: str
    api_key: str
    referral_code: str
    trading_status: str
    status: str
    total_members: int
    active_members: int
    master_accounts: List[dict]
    created_by: str
    created_at: datetime
    updated_at: datetime

class APIKeyGenerate(BaseModel):
    admin_otp: str = Field(..., min_length=4, max_length=10)

class GroupDocument(BaseModel):
    """Database document model for groups"""
    id: Optional[str] = Field(None, alias="_id")
    group_name: str
    company_name: str
    profit_sharing_percent: float
    settlement_cycle: str
    api_key: str
    referral_code: str = Field(..., description="Unique referral code for joining the group")
    trading_status: str = "active"
    status: str = "active"
    master_accounts: List[dict]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }