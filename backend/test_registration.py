#!/usr/bin/env python3
"""
Test script to verify user registration and database operations are working
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.mongodb_service import mongodb_service
from core.database import connect_to_mongo, close_mongo_connection

async def test_user_registration():
    """Test user registration with real database"""
    print("🧪 Testing User Registration with Real Database")
    print("=" * 50)

    # Connect to database
    print("🔄 Connecting to MongoDB...")
    await connect_to_mongo()

    # Test user data
    test_user = {
        "name": "Test User",
        "email": "testuser@example.com",
        "mobile": "+1234567890",
        "password": "testpass123",
        "country": "USA",
        "state": "California",
        "city": "Los Angeles",
        "pin_code": "90210",
        "broker": "Vantage",
        "account_no": "12345678",
        "trading_password": "trading123",
        "referral_code": None
    }

    try:
        # Test 1: Create user
        print("\n🧪 Test 1: Creating new user...")
        result = await mongodb_service.create_user(test_user)
        print(f"Result: {result}")

        if result["status"]:
            user_id = result["data"]["user_id"]
            print(f"✅ User created successfully with ID: {user_id}")

            # Test 2: Verify user exists in database
            print("\n🧪 Test 2: Verifying user exists in database...")
            db = mongodb_service.get_db()
            if db:
                user_doc = await db.users.find_one({"email": test_user["email"]})
                if user_doc:
                    print(f"✅ User found in database:")
                    print(f"   - Name: {user_doc['name']}")
                    print(f"   - Email: {user_doc['email']}")
                    print(f"   - Mobile: {user_doc['mobile']}")
                    print(f"   - Status: {user_doc['status']}")
                    print(f"   - Broker: {user_doc['broker']}")
                    print(f"   - Account: {user_doc['account_no']}")
                else:
                    print("❌ User not found in database!")
            else:
                print("❌ Database connection not available!")

            # Test 3: Test authentication
            print("\n🧪 Test 3: Testing authentication...")
            auth_result = await mongodb_service.authenticate_user(
                test_user["email"],
                test_user["password"]
            )
            print(f"Auth Result: {auth_result}")

            if auth_result["status"]:
                print("✅ Authentication successful")
            else:
                print("❌ Authentication failed")

            # Test 4: Try duplicate registration
            print("\n🧪 Test 4: Testing duplicate registration...")
            duplicate_result = await mongodb_service.create_user(test_user)
            print(f"Duplicate Result: {duplicate_result}")

            if not duplicate_result["status"] and "already exists" in duplicate_result["message"]:
                print("✅ Duplicate prevention working correctly")
            else:
                print("❌ Duplicate prevention not working!")

            # Clean up - remove test user
            print("\n🧹 Cleaning up test data...")
            if db:
                delete_result = await db.users.delete_one({"email": test_user["email"]})
                if delete_result.deleted_count > 0:
                    print("✅ Test user deleted successfully")
                else:
                    print("⚠️ Test user not deleted")

        else:
            print(f"❌ User creation failed: {result['message']}")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

    finally:
        # Close database connection
        print("\n🔌 Closing database connection...")
        await close_mongo_connection()

    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_user_registration())