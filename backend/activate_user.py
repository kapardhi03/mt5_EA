# activate_user.py - Run this script to activate your test user
from backend.utils.mongo import update_document
from backend.core.config import settings

# Update user status to active
result = update_document(
    settings.DATABASE_NAME,
    "users", 
    "email", 
    "test@example.com",
    {
        "status": "active",
        "mobile_verified": True,
        "email_verified": True
    }
)

if result["status"]:
    print("✅ User activated successfully!")
    print("You can now login with email: test@example.com")
else:
    print("❌ Failed to activate user:", result["error"])