# ===================================
# services/master_account_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.core.config import settings
from backend.utils.encryption import encrypt_string
import uuid

class MasterAccountService:
    
    async def create_master_account(self, account_data: dict, created_by: str) -> dict:
        """Create master account"""
        
        try:
            # Encrypt passwords
            encrypted_password = encrypt_string(account_data["password"])
            encrypted_investor_password = None
            if account_data.get("investor_password"):
                encrypted_investor_password = encrypt_string(account_data["investor_password"])
            
            master_record = {
                "master_id": str(uuid.uuid4()),
                "broker": account_data["broker"],
                "server": account_data["server"],
                "account_no": account_data["account_no"],
                "password": encrypted_password,
                "investor_password": encrypted_investor_password,
                "account_type": account_data["account_type"],
                "status": "active",
                "health_status": "unknown",
                "last_ping": None,
                "latency_ms": 0,
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = insert_document(settings.DATABASE_NAME, "master_accounts", master_record)
            
            if result["status"]:
                return {"status": True, "message": "Master account created successfully", "data": master_record}
            else:
                return {"status": False, "message": "Failed to create master account"}
                
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_master_accounts(self) -> dict:
        """Get all master accounts"""
        
        try:
            result = fetch_documents(
                settings.DATABASE_NAME,
                "master_accounts",
                {"status": {"$ne": "deleted"}},
                sort=[("created_at", -1)]
            )
            
            if result["status"]:
                # Clean sensitive data
                for account in result["data"]:
                    account.pop("password", None)
                    account.pop("investor_password", None)
            
            return result
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_master_account_health(self) -> dict:
        """Get master account health status"""
        
        try:
            # Mock health data (replace with real Trade Copier API calls)
            health_data = [
                {
                    "account_id": "master_001",
                    "broker": "IC Markets",
                    "server": "ICMarkets-Demo",
                    "account_no": "12345678",
                    "status": "active",
                    "last_ping": datetime.utcnow(),
                    "latency_ms": 45,
                    "connection_status": "connected",
                    "equity": 125000.0,
                    "profit": 8420.0,
                    "open_positions": 5
                }
            ]
            
            return {"status": True, "data": health_data}
            
        except Exception as e:
            return {"status": False, "error": str(e)}

# Initialize service
master_account_service = MasterAccountService()