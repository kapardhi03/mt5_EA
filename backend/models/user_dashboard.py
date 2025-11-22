# ===================================
# models/user_dashboard.py
# ===================================
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserDashboard(BaseModel):
    total_equity: float
    total_profit: float
    profit_percentage: float
    today_profit: float
    total_withdrawal: float
    running_trades: int
    copy_status: str
    linked_accounts: int

class UserAccount(BaseModel):
    account_id: str
    account_type: str
    broker: str
    server: str
    account_no: str
    copy_status: str
    linked_group: str
    copy_start_date: Optional[datetime]
    opening_balance: float
    current_balance: float
    profit_till_date: float
    running_trades: int

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)