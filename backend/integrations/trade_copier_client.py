# ===================================
# integrations/trade_copier_client.py
# ===================================
import httpx
from typing import Dict, Any, Optional
from backend.core.config import settings

class TradeCopierClient:
    """HTTP client for Trade Copier API integration"""
    
    def __init__(self):
        self.base_url = settings.TRADE_COPIER_BASE_URL
        self.api_key = settings.TRADE_COPIER_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
    
    async def add_master_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add master account to Trade Copier"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/master/add",
                    json=account_data,
                    headers=self.headers
                )
                return {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else ""
                }
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def add_slave_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add slave account to Trade Copier"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/slave/add",
                    json=account_data,
                    headers=self.headers
                )
                return {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else ""
                }
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def connect_slave_to_master(self, slave_id: str, master_id: str) -> Dict[str, Any]:
        """Connect slave account to master account"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/connection/connect",
                    json={"slave_id": slave_id, "master_id": master_id},
                    headers=self.headers
                )
                return {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else ""
                }
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def get_account_performance(self, account_id: str) -> Dict[str, Any]:
        """Get account performance data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/performance/{account_id}",
                    headers=self.headers
                )
                return {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else ""
                }
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}
    
    async def enable_disable_copying(self, account_id: str, status: bool) -> Dict[str, Any]:
        """Enable or disable copying for an account"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/control/toggle/{account_id}",
                    json={"enabled": status},
                    headers=self.headers
                )
                return {
                    "status": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else ""
                }
        except Exception as e:
            return {"status": False, "data": None, "error": str(e)}

# Initialize client
trade_copier_client = TradeCopierClient()