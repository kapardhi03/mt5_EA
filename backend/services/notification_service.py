# ===================================
# services/notification_service.py
# ===================================
from datetime import datetime
from backend.utils.mongo import insert_document, fetch_documents, update_document
from backend.core.config import settings
import uuid

class NotificationService:
    
    async def create_notification(self, notification_data: dict) -> dict:
        """Create notification"""
        
        try:
            notification_record = {
                "notification_id": str(uuid.uuid4()),
                "title": notification_data["title"],
                "message": notification_data["message"],
                "type": notification_data["type"],
                "user_id": notification_data.get("user_id"),
                "group_id": notification_data.get("group_id"),
                "read": False,
                "created_at": datetime.utcnow()
            }
            
            result = insert_document(settings.DATABASE_NAME, "notifications", notification_record)
            
            return result
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def get_user_notifications(self, user_id: str) -> dict:
        """Get user notifications"""
        
        try:
            result = fetch_documents(
                settings.DATABASE_NAME,
                "notifications",
                {"$or": [{"user_id": user_id}, {"user_id": None}]},
                sort=[("created_at", -1)],
                limit=50
            )
            
            return result
            
        except Exception as e:
            return {"status": False, "error": str(e)}
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        """Mark notification as read"""
        
        try:
            result = update_document(
                settings.DATABASE_NAME,
                "notifications",
                "notification_id",
                notification_id,
                {"read": True}
            )
            
            return result
            
        except Exception as e:
            return {"status": False, "error": str(e)}

# Initialize service
notification_service = NotificationService()