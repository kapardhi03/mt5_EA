# ===================================
# services/group_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import insert_document, fetch_documents, update_document, delete_document
from backend.core.security import get_current_user
from backend.core.config import settings
from backend.integrations.trade_copier_client import trade_copier_client
from backend.utils.encryption import encrypt_string, decrypt_string
import uuid
import secrets
import string

class GroupService:
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def clean_group_data(self, group_data: dict) -> dict:
        """Clean group data for API response"""
        cleaned_data = group_data.copy()
        
        # Decrypt master account passwords for internal use only
        if "master_accounts" in cleaned_data:
            for account in cleaned_data["master_accounts"]:
                # Don't expose actual passwords in response
                account.pop("password", None)
                account.pop("investor_password", None)
        
        # Ensure _id is string if present
        if "_id" in cleaned_data:
            cleaned_data["_id"] = str(cleaned_data["_id"])
            
        return cleaned_data
    
    async def create_group(self, group_data: dict, created_by: str) -> dict:
        """Create a new group"""
        
        # Check if group name already exists
        existing_group = fetch_documents(
            settings.DATABASE_NAME,
            "groups",
            {"group_name": group_data["group_name"]}
        )
        
        if existing_group["status"] and existing_group["data"]:
            return {"status": False, "message": "Group with this name already exists"}
        
        # Encrypt master account passwords
        encrypted_master_accounts = []
        for account in group_data["master_accounts"]:
            encrypted_account = account.copy()
            encrypted_account["password"] = encrypt_string(account["password"])
            if account.get("investor_password"):
                encrypted_account["investor_password"] = encrypt_string(account["investor_password"])
            encrypted_master_accounts.append(encrypted_account)
        
        # Generate API key
        api_key = self.generate_api_key()
        
        # Create group record
        group_record = {
            "group_id": str(uuid.uuid4()),
            "group_name": group_data["group_name"],
            "company_name": group_data["company_name"],
            "profit_sharing_percent": group_data["profit_sharing_percent"],
            "settlement_cycle": group_data["settlement_cycle"],
            "api_key": api_key,
            "trading_status": "paused",  # Start paused by default
            "status": "active",
            "created_by": created_by,
            "master_accounts": encrypted_master_accounts,
            "total_members": 0,
            "active_members": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert group into database
        result = insert_document(settings.DATABASE_NAME, "groups", group_record)
        
        if result["status"]:
            # Create master accounts in Trade Copier
            trade_copier_master_ids = []
            for account in group_data["master_accounts"]:
                copier_result = await self.create_master_in_trade_copier(account, group_record["group_id"])
                if copier_result["status"]:
                    trade_copier_master_ids.append(copier_result["data"]["master_id"])
            
            # Update group with Trade Copier master IDs
            if trade_copier_master_ids:
                for i, master_id in enumerate(trade_copier_master_ids):
                    group_record["master_accounts"][i]["trade_copier_master_id"] = master_id
                
                # Update in database
                update_document(
                    settings.DATABASE_NAME,
                    "groups",
                    "group_id",
                    group_record["group_id"],
                    {"master_accounts": group_record["master_accounts"]}
                )
            
            # Clean and return group data
            clean_group = self.clean_group_data(group_record)
            return {"status": True, "message": "Group created successfully", "data": clean_group}
        else:
            return {"status": False, "message": "Failed to create group", "error": result["error"]}
    
    async def create_master_in_trade_copier(self, account_data: dict, group_id: str) -> dict:
        """Create master account in Trade Copier system"""
        try:
            trade_copier_data = {
                "account_no": account_data["account_no"],
                "broker": account_data["broker"],
                "server": account_data["server"],
                "password": account_data["password"],
                "investor_password": account_data.get("investor_password"),
                "account_type": account_data["account_type"],
                "group_reference": group_id
            }
            
            result = await trade_copier_client.add_master_account(trade_copier_data)
            return result
            
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def get_groups(self, user_id: str, user_role: str) -> dict:
        """Get groups based on user role"""
        
        if user_role == "admin":
            # Admin can see all groups
            query = {}
        else:
            # Other users can only see groups they created or are members of
            query = {"created_by": user_id}
        
        result = fetch_documents(
            settings.DATABASE_NAME,
            "groups",
            query,
            sort=[("created_at", -1)]
        )
        
        if result["status"]:
            clean_groups = [self.clean_group_data(group) for group in result["data"]]
            return {"status": True, "data": clean_groups}
        else:
            return {"status": False, "message": "Failed to fetch groups", "error": result["error"]}
    
    async def get_group_by_id(self, group_id: str) -> dict:
        """Get group by ID"""
        result = fetch_documents(settings.DATABASE_NAME, "groups", {"group_id": group_id})
        
        if result["status"] and result["data"]:
            group = result["data"][0]
            clean_group = self.clean_group_data(group)
            return {"status": True, "data": clean_group}
        return {"status": False, "message": "Group not found"}
    
    async def update_group(self, group_id: str, update_data: dict, user_id: str) -> dict:
        """Update group"""
        # Check if group exists and user has permission
        group_result = await self.get_group_by_id(group_id)
        if not group_result["status"]:
            return {"status": False, "message": "Group not found"}
        
        group = group_result["data"]
        
        # Check permission (only creator or admin can update)
        if group["created_by"] != user_id:
            # TODO: Check if user is admin
            pass
        
        # Update group
        result = update_document(
            settings.DATABASE_NAME,
            "groups",
            "group_id",
            group_id,
            update_data
        )
        
        if result["status"]:
            # Get updated group
            updated_group = await self.get_group_by_id(group_id)
            return {"status": True, "message": "Group updated successfully", "data": updated_group["data"]}
        else:
            return {"status": False, "message": "Failed to update group", "error": result["error"]}
    
    async def toggle_trading_status(self, group_id: str, status: str, user_id: str) -> dict:
        """Start/Stop trading for a group"""
        
        # Verify group exists
        group_result = await self.get_group_by_id(group_id)
        if not group_result["status"]:
            return {"status": False, "message": "Group not found"}
        
        group = group_result["data"]
        
        # Update trading status in database
        update_data = {"trading_status": status}
        result = update_document(
            settings.DATABASE_NAME,
            "groups",
            "group_id",
            group_id,
            update_data
        )
        
        if result["status"]:
            # TODO: Update Trade Copier to enable/disable copying for all group members
            
            return {"status": True, "message": f"Trading status updated to {status}"}
        else:
            return {"status": False, "message": "Failed to update trading status"}
    
    async def regenerate_api_key(self, group_id: str, user_id: str) -> dict:
        """Regenerate API key for group"""
        
        # Verify group exists and user has permission
        group_result = await self.get_group_by_id(group_id)
        if not group_result["status"]:
            return {"status": False, "message": "Group not found"}
        
        # Generate new API key
        new_api_key = self.generate_api_key()
        
        # Update in database
        result = update_document(
            settings.DATABASE_NAME,
            "groups",
            "group_id",
            group_id,
            {"api_key": new_api_key}
        )
        
        if result["status"]:
            return {"status": True, "message": "API key regenerated successfully", "data": {"api_key": new_api_key}}
        else:
            return {"status": False, "message": "Failed to regenerate API key"}

# Initialize service
group_service = GroupService()