# ===================================
# services/trading_service.py (Proxy to Trade Copier)
# ===================================
from backend.integrations.trade_copier_client import trade_copier_client
from backend.services.member_service import member_service
from backend.services.group_service import group_service

class TradingService:
    """Service to aggregate trading data from Trade Copier API"""
    
    async def get_live_trading_metrics(self, user_id: str, user_role: str) -> dict:
        """Get live trading metrics for dashboard"""
        
        try:
            # For now, return mock data - replace with actual Trade Copier API calls
            mock_metrics = {
                "total_equity": 125000.0,
                "total_profit": 15420.0,
                "today_profit": 1250.0,
                "running_trades": 12,
                "active_members": 25,
                "pending_settlements": 2
            }
            
            # TODO: Integrate with actual Trade Copier API
            # live_data = await trade_copier_client.get_live_metrics()
            
            return {"status": True, "data": mock_metrics}
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_live_positions(self, group_id: str = None) -> dict:
        """Get current open positions"""
        
        try:
            # Mock data - replace with Trade Copier API
            mock_positions = [
                {
                    "symbol": "EURUSD",
                    "type": "buy",
                    "volume": 1.0,
                    "open_price": 1.0845,
                    "current_price": 1.0867,
                    "profit": 220.0,
                    "account_id": "12345678"
                },
                {
                    "symbol": "GBPUSD", 
                    "type": "sell",
                    "volume": 0.5,
                    "open_price": 1.2654,
                    "current_price": 1.2631,
                    "profit": 115.0,
                    "account_id": "12345678"
                }
            ]
            
            return {"status": True, "data": mock_positions}
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_member_performance(self, member_id: str) -> dict:
        """Get detailed member performance data"""
        
        try:
            # Mock performance data
            mock_performance = {
                "total_trades": 245,
                "winning_trades": 147,
                "win_rate": 60.0,
                "total_profit": 8420.0,
                "today_profit": 340.0,
                "weekly_profit": 1250.0,
                "monthly_profit": 3420.0,
                "max_drawdown": -1200.0,
                "current_equity": 28420.0
            }
            
            return {"status": True, "data": mock_performance}
            
        except Exception as e:
            return {"status": False, "error": str(e)}

# Initialize service  
trading_service = TradingService()