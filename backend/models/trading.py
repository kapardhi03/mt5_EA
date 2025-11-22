# ===================================
# models/trading.py
# ===================================
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LivePosition(BaseModel):
    symbol: str
    type: str  # buy/sell
    volume: float
    open_price: float
    current_price: float
    profit: float
    account_id: str

class TradingMetrics(BaseModel):
    total_equity: float
    total_profit: float
    today_profit: float
    running_trades: int
    active_members: int

class MasterAccountHealth(BaseModel):
    account_id: str
    broker: str
    server: str
    status: str
    last_ping: datetime
    latency_ms: int
    connection_status: str