# ===================================
# services/settlement_service.py
# ===================================
from datetime import datetime, timedelta
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.core.config import settings
from backend.services.group_service import group_service
from backend.services.user_service import user_service
from backend.integrations.trade_copier_client import trade_copier_client
import uuid

class SettlementService:
    
    async def calculate_profit_sharing(self, group_id: str, period_from: datetime, period_to: datetime) -> dict:
        """Calculate profit sharing for a group in given period"""
        
        # Get group details
        group_result = await group_service.get_group_by_id(group_id)
        if not group_result["status"]:
            return {"status": False, "message": "Group not found"}
        
        group = group_result["data"]
        
        # Get profit data from Trade Copier API (mock for now)
        profit_data = await self.get_group_profit_from_trade_copier(group_id, period_from, period_to)
        
        if not profit_data["status"]:
            return {"status": False, "message": "Failed to get profit data"}
        
        total_profit = profit_data["data"]["total_profit"]
        profit_share_amount = total_profit * (group["profit_sharing_percent"] / 100)
        
        return {
            "status": True,
            "data": {
                "total_profit": total_profit,
                "profit_share_percent": group["profit_sharing_percent"],
                "amount_due": profit_share_amount,
                "period_from": period_from,
                "period_to": period_to
            }
        }
    
    async def get_group_profit_from_trade_copier(self, group_id: str, period_from: datetime, period_to: datetime) -> dict:
        """Get profit data from Trade Copier API"""
        try:
            # This will call the actual Trade Copier API
            # For now, return mock data
            mock_profit = 15000.0  # $15,000 profit in period
            
            return {
                "status": True,
                "data": {
                    "total_profit": mock_profit,
                    "member_profits": [
                        {"member_id": "mem1", "profit": 7500.0},
                        {"member_id": "mem2", "profit": 7500.0}
                    ]
                }
            }
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def submit_settlement(self, settlement_data: dict, submitted_by: str) -> dict:
        """Submit a settlement request"""
        
        # Calculate profit sharing
        calculation = await self.calculate_profit_sharing(
            settlement_data["group_id"],
            settlement_data["period_from"],
            settlement_data["period_to"]
        )
        
        if not calculation["status"]:
            return calculation
        
        calc_data = calculation["data"]
        
        # Create settlement record
        settlement_record = {
            "settlement_id": str(uuid.uuid4()),
            "group_id": settlement_data["group_id"],
            "period_from": settlement_data["period_from"],
            "period_to": settlement_data["period_to"],
            "total_profit": calc_data["total_profit"],
            "profit_share_percent": calc_data["profit_share_percent"],
            "amount_due": calc_data["amount_due"],
            "amount_paid": settlement_data["amount_paid"],
            "payment_method": settlement_data["payment_method"],
            "payment_reference": settlement_data["payment_reference"],
            "payment_proof_file": settlement_data.get("payment_proof_file"),
            "status": "pending",
            "submitted_by": submitted_by,
            "approved_by": None,
            "auto_paused": False,
            "submitted_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = insert_document(settings.DATABASE_NAME, "settlements", settlement_record)
        
        if result["status"]:
            return {"status": True, "message": "Settlement submitted successfully", "data": settlement_record}
        else:
            return {"status": False, "message": "Failed to submit settlement"}
    
    async def get_pending_settlements(self) -> dict:
        """Get all pending settlements"""
        
        result = fetch_documents(
            settings.DATABASE_NAME,
            "settlements",
            {"status": "pending"},
            sort=[("submitted_at", -1)]
        )
        
        if result["status"]:
            # Enrich with group names
            enriched_settlements = []
            for settlement in result["data"]:
                group_result = await group_service.get_group_by_id(settlement["group_id"])
                if group_result["status"]:
                    settlement["group_name"] = group_result["data"]["group_name"]
                enriched_settlements.append(settlement)
            
            return {"status": True, "data": enriched_settlements}
        else:
            return {"status": False, "message": "Failed to fetch settlements"}
    
    async def approve_settlement(self, settlement_id: str, approval_data: dict, admin_id: str) -> dict:
        """Approve or reject settlement with OTP verification"""
        
        # TODO: Verify OTP first
        
        # Update settlement status
        update_data = {
            "status": approval_data["status"],
            "approved_by": admin_id,
            "approved_at": datetime.utcnow(),
            "remarks": approval_data.get("remarks")
        }
        
        result = update_document(
            settings.DATABASE_NAME,
            "settlements",
            "settlement_id",
            settlement_id,
            update_data
        )
        
        if result["status"] and approval_data["status"] == "approved":
            # Resume group trading if it was auto-paused
            await self.resume_group_if_paused(settlement_id)
            
            return {"status": True, "message": "Settlement approved successfully"}
        else:
            return {"status": False, "message": "Failed to update settlement"}
    
    async def resume_group_if_paused(self, settlement_id: str) -> dict:
        """Resume group trading if it was auto-paused"""
        # Get settlement details
        settlement_result = fetch_documents(
            settings.DATABASE_NAME,
            "settlements", 
            {"settlement_id": settlement_id}
        )
        
        if settlement_result["status"] and settlement_result["data"]:
            settlement = settlement_result["data"][0]
            group_id = settlement["group_id"]
            
            # Resume trading for the group
            await group_service.toggle_trading_status(group_id, "active", "system")
        
        return {"status": True}

# Initialize service
settlement_service = SettlementService()
