"""
Copy Trading Platform Models
Complete data models for Users, Groups, Accounts, Trades, and Reports
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    GROUP_LEADER = "group_leader"
    MASTER = "master"


class AccountType(str, Enum):
    CENT = "cent"
    STANDARD = "standard"
    RAW = "raw"
    PRO = "pro"


class CopyStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    PAUSED = "paused"
    STOPPED = "stopped"


class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class SettlementStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    REJECTED = "rejected"


# User Model
class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: str
    mobile: str
    password_hash: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING

    # Personal Information
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pin_code: Optional[str] = None

    # Verification
    email_verified: bool = False
    mobile_verified: bool = False
    kyc_status: Optional[str] = "pending"  # pending, verified, rejected

    # Group Assignment (user can only be in one group)
    group_id: Optional[str] = None
    group_join_date: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


# Trading Account Model
class TradingAccount(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    group_id: Optional[str] = None

    # Broker Information
    broker: str  # Exness, Vantage, etc.
    server: str
    account_number: str
    account_type: AccountType
    leverage: int = 1000
    currency: str = "USD"

    # Account Details
    trading_password_hash: str  # Encrypted
    opening_balance: float = 0.0
    current_balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0

    # Copy Trading
    copy_status: CopyStatus = CopyStatus.PENDING
    copy_start_date: Optional[datetime] = None
    profit_since_copy_start: float = 0.0
    total_profit: float = 0.0
    total_withdrawal: float = 0.0
    running_trades_count: int = 0

    # IB/Partner Information
    partner_id: Optional[str] = None
    ib_change_proof: Optional[str] = None  # File path
    ib_change_status: str = "pending"  # pending, approved, rejected

    # Status and Errors
    status: str = "pending"  # pending, approved, active, suspended
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Trading Group Model
class TradingGroup(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_name: str
    company_name: str
    description: Optional[str] = None

    # Group Leader/Admin
    group_leader_id: str  # User ID of group leader
    created_by: str  # Admin who created the group

    # Settlement Configuration
    settlement_cycle: str = "monthly"  # daily, weekly, monthly
    profit_sharing_percentage: float = 80.0  # Percentage for members

    # Group Statistics
    active_members: int = 0
    total_members: int = 0
    total_equity: float = 0.0
    total_profit: float = 0.0
    today_profit: float = 0.0
    pending_settlement_amount: float = 0.0

    # Master Account Configuration
    master_account_id: Optional[str] = None
    api_key: Optional[str] = None
    api_key_status: str = "inactive"  # active, inactive, expired

    # Trading Controls
    trading_status: str = "active"  # active, paused, stopped
    auto_pause_rules: Dict[str, Any] = {}

    # Settlement Information
    last_settlement_date: Optional[datetime] = None
    next_settlement_date: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Master Account Model
class MasterAccount(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str
    account_name: str

    # Account Details
    broker: str
    server: str
    account_number: str
    trading_password_hash: str

    # Performance Metrics
    balance: float = 0.0
    equity: float = 0.0
    profit: float = 0.0
    running_trades: int = 0

    # Health Monitoring
    latency_ms: float = 0.0
    last_heartbeat: Optional[datetime] = None
    status: str = "active"  # active, inactive, error

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Trade Model
class Trade(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    # Trade Identification
    master_order_id: str
    slave_order_id: Optional[str] = None
    group_id: str
    user_id: str
    account_id: str

    # Trade Details
    symbol: str
    trade_type: TradeType
    volume: float
    open_price: float
    close_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    # Trade Status
    status: str = "open"  # open, closed, failed
    is_manual: bool = False  # Manual vs Copied trade

    # Profit/Loss
    profit: float = 0.0
    commission: float = 0.0
    swap: float = 0.0

    # Timestamps
    open_time: datetime = Field(default_factory=datetime.now)
    close_time: Optional[datetime] = None

    # Error Handling
    error_message: Optional[str] = None
    retry_count: int = 0

    created_at: datetime = Field(default_factory=datetime.now)


# Settlement Model
class Settlement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str

    # Settlement Period
    period_start: datetime
    period_end: datetime
    settlement_date: datetime

    # Financial Details
    total_profit: float
    profit_sharing_percentage: float
    amount_due: float
    amount_paid: float = 0.0

    # Payment Information
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None  # UTR/Reference
    payment_proof: Optional[str] = None  # File path

    # Status and Approval
    status: SettlementStatus = SettlementStatus.PENDING
    submitted_by: Optional[str] = None
    approved_by: Optional[str] = None
    otp_verification_id: Optional[str] = None

    # Auto Pause Configuration
    auto_pause_on_settlement: bool = False
    resume_time: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Error Log Model
class ErrorLog(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    # Error Context
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    group_id: Optional[str] = None
    master_account_id: Optional[str] = None

    # Trade Context
    symbol: Optional[str] = None
    trade_side: Optional[str] = None
    volume_attempted: Optional[float] = None

    # Error Details
    error_code: str
    error_message: str
    server_response_code: Optional[int] = None

    # Resolution
    retry_count: int = 0
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)


# Support Ticket Model
class SupportTicket(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str

    # Ticket Details
    subject: str
    description: str
    priority: str = "medium"  # low, medium, high, urgent
    category: str = "general"  # general, trading, account, payment

    # Status
    status: str = "open"  # open, in_progress, resolved, closed
    assigned_to: Optional[str] = None

    # Communication
    messages: List[Dict[str, Any]] = []

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# API Configuration Model
class APIConfiguration(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str

    # API Details
    api_key: str
    api_secret: str
    environment: str = "demo"  # demo, live

    # Broker Specific
    broker: str
    server: str

    # Status
    status: str = "active"  # active, inactive, expired
    last_used: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)


# Allocation Rules Model
class AllocationRule(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str

    # Rule Configuration
    rule_name: str
    allocation_type: str = "percentage"  # percentage, fixed, equity_based
    allocation_value: float

    # Conditions
    min_equity: Optional[float] = None
    max_equity: Optional[float] = None
    symbols: Optional[List[str]] = None  # If symbol-specific

    # Status
    active: bool = True

    created_at: datetime = Field(default_factory=datetime.now)


# Symbol Mapping Model
class SymbolMapping(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str

    # Symbol Details
    master_symbol: str
    slave_symbol: str
    volume_multiplier: float = 1.0

    # Filters
    min_volume: Optional[float] = None
    max_volume: Optional[float] = None

    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)