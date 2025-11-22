# ===================================
# services/support_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.core.config import settings
import uuid

class SupportService:
    
    async def create_ticket(self, ticket_data: dict, user_id: str) -> dict:
        """Create support ticket"""
        
        try:
            ticket_record = {
                "ticket_id": str(uuid.uuid4()),
                "subject": ticket_data["subject"],
                "message": ticket_data["message"],
                "priority": ticket_data["priority"],
                "category": ticket_data["category"],
                "status": "open",
                "created_by": user_id,
                "assigned_to": None,
                "responses": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = insert_document(settings.DATABASE_NAME, "support_tickets", ticket_record)
            
            if result["status"]:
                return {"status": True, "message": "Support ticket created successfully", "data": ticket_record}
            else:
                return {"status": False, "message": "Failed to create ticket"}
                
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_user_tickets(self, user_id: str) -> dict:
        """Get user's support tickets"""
        
        try:
            result = fetch_documents(
                settings.DATABASE_NAME,
                "support_tickets",
                {"created_by": user_id},
                sort=[("created_at", -1)]
            )
            
            return result
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_faqs(self) -> dict:
        """Get frequently asked questions"""
        
        try:
            # Mock FAQ data (replace with database storage)
            faqs = [
                {
                    "id": "1",
                    "question": "How do I link my MT5 account?",
                    "answer": "Go to Account Management > Add New Account, select your broker, enter account details, and wait for approval.",
                    "category": "Account Management",
                    "order": 1
                },
                {
                    "id": "2", 
                    "question": "When will my copy trading start?",
                    "answer": "Copy trading starts after your account is approved and the group trading is active. You'll receive a notification.",
                    "category": "Copy Trading",
                    "order": 2
                },
                {
                    "id": "3",
                    "question": "How are profits calculated?",
                    "answer": "Profits are calculated based only on copied trades. Manual trades are excluded from profit sharing calculations.",
                    "category": "Profit Sharing",
                    "order": 3
                }
            ]
            
            return {"status": True, "data": faqs}
            
        except Exception as e:
            return {"status": False, "error": str(e)}

# Initialize service
support_service = SupportService()
