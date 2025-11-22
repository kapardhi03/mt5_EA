# ===================================
# services/member_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.core.config import settings
from backend.services.group_service import group_service
from backend.services.user_service import user_service
from backend.integrations.trade_copier_client import trade_copier_client
from backend.utils.encryption import encrypt_string, decrypt_string
import uuid

class MemberService:
    
    def clean_member_data(self, member_data: dict) -> dict:
        """Clean member data for API response"""
        cleaned_data = member_data.copy()
        
        # Remove sensitive password data
        cleaned_data.pop("password", None)
        
        # Ensure _id is string if present
        if "_id" in cleaned_data:
            cleaned_data["_id"] = str(cleaned_data["_id"])
            
        return cleaned_data
    
    async def add_member_to_group(self, member_data: dict, added_by: str) -> dict:
        """Add a member to a group"""
        
        # Verify user exists
        user_result = await user_service.get_user_by_id(member_data["user_id"])
        if not user_result["status"]:
            return {"status": False, "message": "User not found"}
        
        user = user_result["data"]
        
        # Verify group exists
        group_result = await group_service.get_group_by_id(member_data["group_id"])
        if not group_result["status"]:
            return {"status": False, "message": "Group not found"}
        
        group = group_result["data"]
        
        # Check if user is already a member of this group
        existing_member = fetch_documents(
            settings.DATABASE_NAME,
            "members",
            {
                "user_id": member_data["user_id"],
                "group_id": member_data["group_id"],
                "status": {"$ne": "deleted"}
            }
        )
        
        if existing_member["status"] and existing_member["data"]:
            return {"status": False, "message": "User is already a member of this group"}
        
        # Verify MT5 account (basic validation)
        account_verification = await self.verify_mt5_account(
            member_data["broker"],
            member_data["server"], 
            member_data["account_no"],
            member_data["password"]
        )
        
        if not account_verification["status"]:
            return {"status": False, "message": f"MT5 account verification failed: {account_verification['message']}"}
        
        # Encrypt password
        encrypted_password = encrypt_string(member_data["password"])
        
        # Create member record
        member_record = {
            "member_id": str(uuid.uuid4()),
            "user_id": member_data["user_id"],
            "group_id": member_data["group_id"],
            "broker": member_data["broker"],
            "server": member_data["server"],
            "account_no": member_data["account_no"],
            "password": encrypted_password,
            "opening_balance": member_data["opening_balance"],
            "opening_date": datetime.utcnow(),
            "copy_start_date": None,  # Will be set when copying starts
            "status": "active",
            "last_sync": None,
            "last_error": None,
            "allocation_model": member_data["allocation_model"],
            "trade_copier_mapping": {
                "slave_account_id": None,  # Will be set after Trade Copier creation
                "master_account_id": None,
                "copying_enabled": False,
                "last_trade_sync": None
            },
            "added_by": added_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert member into database
        result = insert_document(settings.DATABASE_NAME, "members", member_record)
        
        if result["status"]:
            # Create slave account in Trade Copier
            copier_result = await self.create_slave_in_trade_copier(member_record, group)
            
            if copier_result["status"]:
                # Update member with Trade Copier information
                trade_copier_mapping = {
                    "slave_account_id": copier_result["data"]["slave_id"],
                    "master_account_id": group["master_accounts"][0].get("trade_copier_master_id"),
                    "copying_enabled": False,
                    "last_trade_sync": None
                }
                
                update_document(
                    settings.DATABASE_NAME,
                    "members",
                    "member_id",
                    member_record["member_id"],
                    {"trade_copier_mapping": trade_copier_mapping}
                )
                
                member_record["trade_copier_mapping"] = trade_copier_mapping
            
            # Update group member count
            await self.update_group_member_count(member_data["group_id"])
            
            # Prepare response with user and group details
            member_response = await self.enrich_member_data(member_record)
            
            return {"status": True, "message": "Member added successfully", "data": member_response}
        else:
            return {"status": False, "message": "Failed to add member", "error": result["error"]}
    
    async def verify_mt5_account(self, broker: str, server: str, account_no: str, password: str) -> dict:
        """Verify MT5 account credentials"""
        # This is a placeholder for MT5 account verification
        # In a real implementation, you would connect to the MT5 terminal or broker API
        # For now, we'll just do basic validation
        
        try:
            # Basic validation
            if not all([broker, server, account_no, password]):
                return {"status": False, "message": "All account fields are required"}
            
            if not account_no.isdigit():
                return {"status": False, "message": "Account number must be numeric"}
            
            if len(password) < 4:
                return {"status": False, "message": "Password must be at least 4 characters"}
            
            # TODO: Implement actual MT5 connection verification
            # For development, we'll assume verification passed
            return {"status": True, "message": "Account verified successfully"}
            
        except Exception as e:
            return {"status": False, "message": f"Verification failed: {str(e)}"}
    
    async def create_slave_in_trade_copier(self, member_data: dict, group_data: dict) -> dict:
        """Create slave account in Trade Copier system"""
        try:
            trade_copier_data = {
                "account_no": member_data["account_no"],
                "broker": member_data["broker"],
                "server": member_data["server"],
                "password": decrypt_string(member_data["password"]),
                "member_reference": member_data["member_id"],
                "group_reference": group_data["group_id"],
                "allocation_model": member_data["allocation_model"]
            }
            
            result = await trade_copier_client.add_slave_account(trade_copier_data)
            
            if result["status"]:
                # Connect slave to master
                master_account_id = group_data["master_accounts"][0].get("trade_copier_master_id")
                if master_account_id:
                    await trade_copier_client.connect_slave_to_master(
                        result["data"]["slave_id"],
                        master_account_id
                    )
            
            return result
            
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def enrich_member_data(self, member_data: dict) -> dict:
        """Enrich member data with user and group information"""
        enriched_data = self.clean_member_data(member_data.copy())
        
        # Get user details
        user_result = await user_service.get_user_by_id(member_data["user_id"])
        if user_result["status"]:
            user = user_result["data"]
            enriched_data["user_name"] = user["name"]
            enriched_data["mobile"] = user["mobile"]
            enriched_data["email"] = user["email"]
        
        # Get group details
        group_result = await group_service.get_group_by_id(member_data["group_id"])
        if group_result["status"]:
            group = group_result["data"]
            enriched_data["group_name"] = group["group_name"]
        
        return enriched_data
    
    async def get_members(self, group_id: str = None, user_role: str = None) -> dict:
        """Get members with optional group filtering"""
        
        # Build query based on parameters
        query = {"status": {"$ne": "deleted"}}
        
        if group_id:
            query["group_id"] = group_id
        
        result = fetch_documents(
            settings.DATABASE_NAME,
            "members",
            query,
            sort=[("created_at", -1)]
        )
        
        if result["status"]:
            # Enrich member data with user and group details
            enriched_members = []
            for member in result["data"]:
                enriched_member = await self.enrich_member_data(member)
                enriched_members.append(enriched_member)
            
            return {"status": True, "data": enriched_members}
        else:
            return {"status": False, "message": "Failed to fetch members", "error": result["error"]}
    
    async def get_member_by_id(self, member_id: str) -> dict:
        """Get member by ID"""
        result = fetch_documents(settings.DATABASE_NAME, "members", {"member_id": member_id})
        
        if result["status"] and result["data"]:
            member = result["data"][0]
            enriched_member = await self.enrich_member_data(member)
            return {"status": True, "data": enriched_member}
        return {"status": False, "message": "Member not found"}
    
    async def update_member(self, member_id: str, update_data: dict, user_id: str) -> dict:
        """Update member"""
        
        # Verify member exists
        member_result = await self.get_member_by_id(member_id)
        if not member_result["status"]:
            return {"status": False, "message": "Member not found"}
        
        # Update member in database
        result = update_document(
            settings.DATABASE_NAME,
            "members",
            "member_id",
            member_id,
            update_data
        )
        
        if result["status"]:
            # If status changed, update Trade Copier
            if "status" in update_data:
                await self.sync_member_status_to_trade_copier(member_id, update_data["status"])
            
            # Get updated member
            updated_member = await self.get_member_by_id(member_id)
            return {"status": True, "message": "Member updated successfully", "data": updated_member["data"]}
        else:
            return {"status": False, "message": "Failed to update member", "error": result["error"]}
    
    async def sync_member_status_to_trade_copier(self, member_id: str, status: str) -> dict:
        """Sync member status to Trade Copier"""
        try:
            # Get member details
            member_result = await self.get_member_by_id(member_id)
            if not member_result["status"]:
                return {"status": False, "message": "Member not found"}
            
            member = member_result["data"]
            slave_account_id = member["trade_copier_mapping"].get("slave_account_id")
            
            if slave_account_id:
                enabled = status == "active"
                result = await trade_copier_client.enable_disable_copying(slave_account_id, enabled)
                
                if result["status"]:
                    # Update copy start date if enabling for first time
                    if enabled and not member.get("copy_start_date"):
                        update_document(
                            settings.DATABASE_NAME,
                            "members",
                            "member_id",
                            member_id,
                            {"copy_start_date": datetime.utcnow()}
                        )
                
                return result
            else:
                return {"status": False, "message": "Trade Copier mapping not found"}
                
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def update_group_member_count(self, group_id: str) -> dict:
        """Update member counts for a group"""
        
        # Count total members
        total_result = fetch_documents(
            settings.DATABASE_NAME,
            "members",
            {"group_id": group_id, "status": {"$ne": "deleted"}}
        )
        
        # Count active members
        active_result = fetch_documents(
            settings.DATABASE_NAME,
            "members",
            {"group_id": group_id, "status": "active"}
        )
        
        total_count = len(total_result["data"]) if total_result["status"] else 0
        active_count = len(active_result["data"]) if active_result["status"] else 0
        
        # Update group
        update_document(
            settings.DATABASE_NAME,
            "groups",
            "group_id",
            group_id,
            {
                "total_members": total_count,
                "active_members": active_count
            }
        )
        
        return {"status": True, "total": total_count, "active": active_count}
    
    async def get_available_brokers(self) -> dict:
        """Get list of available brokers and servers"""
        
        # This would typically come from a configuration or external service
        # For now, we'll return a static list
        brokers_data = [
            {
                "broker_name": "IC Markets",
                "servers": [
                    {"server_name": "ICMarkets-Demo", "server_address": "demo.icmarkets.com:443", "status": "active"},
                    {"server_name": "ICMarkets-Live01", "server_address": "live01.icmarkets.com:443", "status": "active"},
                    {"server_name": "ICMarkets-Live02", "server_address": "live02.icmarkets.com:443", "status": "active"}
                ],
                "status": "active"
            },
            {
                "broker_name": "FXPRO",
                "servers": [
                    {"server_name": "FxPro-Demo", "server_address": "demo.fxpro.com:443", "status": "active"},
                    {"server_name": "FxPro-Live", "server_address": "live.fxpro.com:443", "status": "active"}
                ],
                "status": "active"
            },
            {
                "broker_name": "XM Global",
                "servers": [
                    {"server_name": "XMGlobal-Demo", "server_address": "demo.xmglobal.com:443", "status": "active"},
                    {"server_name": "XMGlobal-Real", "server_address": "real.xmglobal.com:443", "status": "active"}
                ],
                "status": "active"
            }
        ]
        
        return {"status": True, "data": {"brokers": brokers_data}}

# Initialize service
member_service = MemberService()
