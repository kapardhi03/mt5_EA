"""
Complete database models for MT5 Copy Trading Platform
Based on detailed specifications from 4xengineer.com
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# ===================================
# User Models
# ===================================

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MASTER = "master"
    GROUP_MANAGER = "group_manager"
    ACCOUNTANT = "accountant"
    SUPPORT = "support"

class UserStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    mobile: str
    email: EmailStr
    country: str
    state: str
    city: str
    pin_code: str
    password_hash: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING
    mobile_verified: bool = False
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

# ===================================
# Broker and Account Models
# ===================================

class BrokerType(str, Enum):
    VANTAGE = "vantage"
    EXNESS = "exness"
    XM = "xm"
    FXTM = "fxtm"
    TICKMILL = "tickmill"

class AccountType(str, Enum):
    STANDARD = "standard"
    CENT = "cent"
    RAW = "raw"
    PRO = "pro"
    ECN = "ecn"

class AccountStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ACTIVE = "active"

class TradingAccount(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    account_number: str
    account_type: AccountType
    broker: BrokerType
    server: str
    partner_id: str
    password_hash: str  # Trading password
    investor_password_hash: Optional[str] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    margin: Optional[float] = None
    free_margin: Optional[float] = None
    currency: str = "USD"
    leverage: Optional[int] = None
    lot_multiplier: float = 1.0  # For copy trading
    is_cent_account: bool = False
    status: AccountStatus = AccountStatus.PENDING
    group_id: Optional[str] = None
    is_master: bool = False
    master_account_id: Optional[str] = None  # If this is a slave account
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    connection_status: str = "disconnected"
    error_message: Optional[str] = None

# ===================================
# Group Management Models
# ===================================

class SettlementCycle(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class GroupStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    PENDING = "pending"

class TradingGroup(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_name: str
    company_name: str
    profit_sharing_percentage: int = Field(ge=10, le=100)  # 10-100%
    settlement_cycle: SettlementCycle
    grace_days: int = 2  # T+2 default
    master_accounts: List[str] = []  # List of master account IDs
    api_key: str
    trading_status: GroupStatus = GroupStatus.PENDING
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    total_members: int = 0
    active_members: int = 0
    total_equity: float = 0.0
    total_profit: float = 0.0
    pending_settlement: float = 0.0
    last_settlement_date: Optional[datetime] = None
    next_settlement_date: Optional[datetime] = None

# ===================================
# Member Management Models
# ===================================

class MemberStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"

class GroupMember(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    group_id: str
    account_id: str  # TradingAccount ID
    status: MemberStatus = MemberStatus.PENDING
    start_date: Optional[datetime] = None
    opening_balance: float = 0.0
    current_balance: float = 0.0
    profit_till_date: float = 0.0  # Only from copied trades
    total_withdrawal: float = 0.0
    lot_multiplier: float = 1.0
    copy_settings: Dict[str, Any] = {}  # Copy preferences
    joined_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None  # Admin user ID
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None

# ===================================
# Settlement Models
# ===================================

class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    CRYPTO = "crypto"
    WALLET = "wallet"
    CASH = "cash"

class SettlementStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"

class Settlement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    group_id: str
    settlement_period_start: datetime
    settlement_period_end: datetime
    gross_profit: float
    profit_sharing_percentage: int
    profit_due: float
    amount_paid: float
    payment_method: PaymentMethod
    payment_reference: str  # UTR/Reference number
    payment_proof_url: Optional[str] = None
    submitted_by: str  # User ID
    submitted_at: datetime = Field(default_factory=datetime.now)
    admin_approver: Optional[str] = None  # Admin user ID
    otp_id: Optional[str] = None
    approval_time: Optional[datetime] = None
    status: SettlementStatus = SettlementStatus.PENDING
    auto_pause_triggered: bool = False
    resume_time: Optional[datetime] = None
    comments: Optional[str] = None

# ===================================
# Trading Models
# ===================================

class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    BUY_LIMIT = "buy_limit"
    SELL_LIMIT = "sell_limit"
    BUY_STOP = "buy_stop"
    SELL_STOP = "sell_stop"

class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    CANCELLED = "cancelled"

class Trade(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    master_account_id: str
    slave_account_id: Optional[str] = None  # For copied trades
    group_id: str
    ticket: str  # MT5 ticket number
    symbol: str
    trade_type: TradeType
    volume: float
    open_price: float
    close_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    open_time: datetime
    close_time: Optional[datetime] = None
    profit: Optional[float] = None
    commission: Optional[float] = None
    swap: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    is_copied_trade: bool = False
    original_trade_id: Optional[str] = None  # Reference to master trade
    copy_status: Optional[str] = None  # Success/Failed/Pending
    error_reason: Optional[str] = None

# ===================================
# Master Account Models
# ===================================

class MasterAccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class MasterAccount(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    account_id: str  # Reference to TradingAccount
    group_id: str
    account_number: str
    broker: BrokerType
    server: str
    account_type: AccountType
    netting_hedging: str = "netting"  # netting/hedging
    health_status: MasterAccountStatus = MasterAccountStatus.ACTIVE
    connection_latency: Optional[float] = None  # in milliseconds
    last_heartbeat: Optional[datetime] = None
    open_positions: int = 0
    current_pnl: float = 0.0
    today_pnl: float = 0.0
    total_followers: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ===================================
# Error Logging Models
# ===================================

class ErrorCode(str, Enum):
    AUTH_FAIL = "AUTH_FAIL"
    SYMBOL_DISABLED = "SYMBOL_DISABLED"
    SYMBOL_MAP_MISSING = "SYMBOL_MAP_MISSING"
    MARKET_CLOSED = "MARKET_CLOSED"
    TRADE_CONTEXT_BUSY = "TRADE_CONTEXT_BUSY"
    VOLUME_TOO_SMALL = "VOLUME_TOO_SMALL"
    VOLUME_TOO_BIG = "VOLUME_TOO_BIG"
    VOLUME_STEP_INVALID = "VOLUME_STEP_INVALID"
    HEDGING_NETTING_CONFLICT = "HEDGING_NETTING_CONFLICT"
    NO_MONEY = "NO_MONEY"
    MARGIN_INSUFFICIENT = "MARGIN_INSUFFICIENT"
    SLIPPAGE_REJECT = "SLIPPAGE_REJECT"
    DUPLICATE_SKIPPED = "DUPLICATE_SKIPPED"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    SERVER_ERROR = "SERVER_ERROR"

class ErrorLog(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.now)
    member_id: str
    account_id: str
    group_id: str
    master_account_id: str
    symbol: str
    trade_side: str  # BUY/SELL
    volume_attempted: float
    reason_code: ErrorCode
    reason_detail: str
    server_response_code: Optional[str] = None
    retry_count: int = 0
    resolved: bool = False
    resolved_by: Optional[str] = None  # Admin user ID
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

# ===================================
# Symbol Mapping Models
# ===================================

class SymbolMapping(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    master_symbol: str
    follower_symbol: str
    master_broker: BrokerType
    follower_broker: BrokerType
    digits: int = 5
    tick_size: float = 0.00001
    contract_size: float = 100000.0
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str  # Admin user ID
    is_active: bool = True

# ===================================
# Lot Size Management Models
# ===================================

class LotSizeMethod(str, Enum):
    SAME_AS_MASTER = "same_as_master"
    AUTO_LOT = "auto_lot"
    FIXED_LOT = "fixed_lot"
    MULTIPLY_FROM_MASTER = "multiply_from_master"
    INCREMENTAL = "incremental"

class LotSizeConfig(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    member_id: str
    group_id: str
    method: LotSizeMethod = LotSizeMethod.SAME_AS_MASTER
    fixed_lot_size: Optional[float] = None
    multiplier: float = 1.0
    min_lot: float = 0.01
    max_lot: float = 100.0
    increment_factor: float = 1.0
    volume_step: float = 0.01
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ===================================
# OTP and Security Models
# ===================================

class OTPType(str, Enum):
    MOBILE = "mobile"
    EMAIL = "email"
    ADMIN_APPROVAL = "admin_approval"

class OTPStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"

class OTPRecord(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    mobile_or_email: str
    otp_code: str
    otp_type: OTPType
    purpose: str  # login, settlement_approval, group_toggle, etc.
    user_id: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    status: OTPStatus = OTPStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    verified_at: Optional[datetime] = None

# ===================================
# Audit Trail Models
# ===================================

class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    PAUSE = "pause"
    RESUME = "resume"
    LOGIN = "login"
    LOGOUT = "logout"

class AuditLog(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    action: AuditAction
    entity_type: str  # user, group, settlement, etc.
    entity_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None

# ===================================
# Configuration Models
# ===================================

class SystemConfig(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    key: str
    value: Any
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str  # Admin user ID

# ===================================
# API Response Models
# ===================================

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool