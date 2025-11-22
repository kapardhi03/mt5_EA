# ===================================
# services/user_dashboard_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import fetch_documents, update_document
from backend.core.config import settings
from backend.services.trading_service import trading_service
import uuid

class UserDashboardService:
    
    async def get_user_dashboard(self, user_id: str) -> dict:
        """Get user dashboard data"""
        
        try:
            # Get user's member accounts
            member_result = fetch_documents(
                settings.DATABASE_NAME,
                "members",
                {"user_id": user_id, "status": {"$ne": "deleted"}}
            )
            
            if not member_result["status"]:
                return {"status": False, "message": "Failed to fetch user data"}
            
            members = member_result["data"]
            
            # Calculate dashboard metrics
            total_equity = 0.0
            total_profit = 0.0
            total_withdrawal = 0.0
            running_trades = 0
            
            for member in members:
                # Get trading performance for each account (mock data for now)
                performance = await trading_service.get_member_performance(member["member_id"])
                if performance["status"]:
                    perf_data = performance["data"]
                    total_equity += perf_data.get("current_equity", 0)
                    total_profit += perf_data.get("total_profit", 0)
                    running_trades += perf_data.get("active_trades", 0)
            
            # Calculate profit percentage
            total_investment = sum(member["opening_balance"] for member in members)
            profit_percentage = (total_profit / total_investment * 100) if total_investment > 0 else 0
            
            # Mock today's profit (replace with real calculation)
            today_profit = total_profit * 0.02  # 2% of total profit as today's
            
            dashboard_data = {
                "total_equity": total_equity,
                "total_profit": total_profit,
                "profit_percentage": round(profit_percentage, 2),
                "today_profit": today_profit,
                "total_withdrawal": total_withdrawal,
                "running_trades": running_trades,
                "copy_status": "active" if any(m["status"] == "active" for m in members) else "inactive",
                "linked_accounts": len(members)
            }
            
            return {"status": True, "data": dashboard_data}
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_user_accounts(self, user_id: str) -> dict:
        """Get user's linked accounts"""
        
        try:
            # Get user's member accounts with group info
            member_result = fetch_documents(
                settings.DATABASE_NAME,
                "members",
                {"user_id": user_id, "status": {"$ne": "deleted"}}
            )
            
            if not member_result["status"]:
                return {"status": False, "message": "Failed to fetch accounts"}
            
            accounts = []
            for member in member_result["data"]:
                # Get group name
                group_result = fetch_documents(
                    settings.DATABASE_NAME,
                    "groups",
                    {"group_id": member["group_id"]}
                )
                
                group_name = "Unknown Group"
                if group_result["status"] and group_result["data"]:
                    group_name = group_result["data"][0]["group_name"]
                
                # Get performance data
                performance = await trading_service.get_member_performance(member["member_id"])
                current_balance = member["opening_balance"]
                profit_till_date = 0.0
                running_trades = 0
                
                if performance["status"]:
                    perf_data = performance["data"]
                    current_balance = perf_data.get("current_equity", member["opening_balance"])
                    profit_till_date = perf_data.get("total_profit", 0)
                    running_trades = perf_data.get("active_trades", 0)
                
                account_data = {
                    "account_id": member["member_id"],
                    "account_type": "Standard",  # Mock data
                    "broker": member["broker"],
                    "server": member["server"],
                    "account_no": f"****{member['account_no'][-4:]}",  # Masked
                    "copy_status": member["status"],
                    "linked_group": group_name,
                    "copy_start_date": member.get("copy_start_date"),
                    "opening_balance": member["opening_balance"],
                    "current_balance": current_balance,
                    "profit_till_date": profit_till_date,
                    "running_trades": running_trades
                }
                accounts.append(account_data)
            
            return {"status": True, "data": accounts}
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_user_portfolio(self, user_id: str) -> dict:
        """Get user portfolio with trade history"""
        
        try:
            # Mock portfolio data (replace with real Trade Copier API calls)
            portfolio_data = {
                "daily_pnl": [
                    {"date": "2025-09-15", "profit": 245.50},
                    {"date": "2025-09-14", "profit": -89.25},
                    {"date": "2025-09-13", "profit": 156.75},
                    {"date": "2025-09-12", "profit": 298.30},
                    {"date": "2025-09-11", "profit": 78.90}
                ],
                "weekly_pnl": [
                    {"week": "2025-W37", "profit": 1245.50},
                    {"week": "2025-W36", "profit": 892.25},
                    {"week": "2025-W35", "profit": 1567.75}
                ],
                "trade_history": [
                    {
                        "trade_id": "T001",
                        "symbol": "EURUSD",
                        "type": "buy",
                        "volume": 1.0,
                        "open_price": 1.0845,
                        "close_price": 1.0867,
                        "profit": 220.0,
                        "open_time": "2025-09-15T08:30:00Z",
                        "close_time": "2025-09-15T12:45:00Z"
                    },
                    {
                        "trade_id": "T002", 
                        "symbol": "GBPUSD",
                        "type": "sell",
                        "volume": 0.5,
                        "open_price": 1.2654,
                        "close_price": 1.2631,
                        "profit": 115.0,
                        "open_time": "2025-09-15T09:15:00Z",
                        "close_time": "2025-09-15T11:30:00Z"
                    }
                ],
                "net_return": {
                    "total_return": 3420.75,
                    "return_percentage": 8.45,
                    "best_trade": 298.30,
                    "worst_trade": -125.40,
                    "avg_trade": 45.67
                }
            }
            
            return {"status": True, "data": portfolio_data}
            
        except Exception as e:
            return {"status": False, "error": str(e)}

# Initialize service
user_dashboard_service = UserDashboardService()