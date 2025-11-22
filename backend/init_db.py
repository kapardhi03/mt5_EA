#!/usr/bin/env python3
"""
Initialize database with demo data for testing
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import connect_to_mongo, get_database
from backend.services.mongodb_service import mongodb_service

async def create_demo_users():
    """Create demo users for testing"""

    # Demo user data
    demo_users = [
        {
            "name": "John Doe",
            "mobile": "+918888888888",
            "email": "admin@4xengineer.com",
            "country": "India",
            "state": "Maharashtra",
            "city": "Mumbai",
            "pin_code": "400001",
            "password": "admin123",
            "role": "admin"
        },
        {
            "name": "Jane Smith",
            "mobile": "+917777777777",
            "email": "user@4xengineer.com",
            "country": "India",
            "state": "Karnataka",
            "city": "Bangalore",
            "pin_code": "560001",
            "password": "user123",
            "role": "user"
        },
        {
            "name": "Master Trader",
            "mobile": "+916666666666",
            "email": "master@4xengineer.com",
            "country": "India",
            "state": "Delhi",
            "city": "New Delhi",
            "pin_code": "110001",
            "password": "master123",
            "role": "master"
        }
    ]

    print("🚀 Creating demo users...")

    for user_data in demo_users:
        print(f"Creating user: {user_data['name']} ({user_data['email']})")
        result = await mongodb_service.create_user(user_data)

        if result["status"]:
            print(f"✅ User created successfully: {user_data['email']}")

            # Update user status to active for testing
            db = mongodb_service.get_db()
            if db is not None:
                await db.users.update_one(
                    {"email": user_data['email']},
                    {"$set": {"status": "active", "mobile_verified": True, "email_verified": True}}
                )
                print(f"✅ User activated: {user_data['email']}")
        else:
            print(f"❌ Failed to create user {user_data['email']}: {result['message']}")

    print("\n🎉 Demo data initialization complete!")
    print("\nYou can now login with:")
    print("Admin: admin@4xengineer.com / admin123")
    print("User: user@4xengineer.com / user123")
    print("Master: master@4xengineer.com / master123")

async def main():
    """Main function"""
    print("🔄 Connecting to MongoDB...")
    await connect_to_mongo()

    print("🔄 Initializing database with demo data...")
    await create_demo_users()

if __name__ == "__main__":
    asyncio.run(main())