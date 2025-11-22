#!/usr/bin/env python3
"""
Clean Database Setup for MT5 Copy Trading Platform
This script will drop all existing collections and create fresh, clean collections
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import connect_to_mongo, get_database
from backend.services.mongodb_service import mongodb_service

async def clean_database():
    """Drop all existing collections and create fresh ones"""
    print("🧹 Starting database cleanup...")

    # Connect to database
    await connect_to_mongo()
    db = get_database()

    if db is None:
        print("❌ Database connection failed")
        return

    print("🗑️ Dropping existing collections...")

    # List of collections to drop
    collections_to_drop = [
        'users',
        'groups',
        'members',
        'settlements',
        'trades',
        'master_accounts',
        'trading_accounts',
        'error_logs',
        'symbol_mappings',
        'lot_size_configs',
        'otp_records',
        'audit_logs',
        'system_configs'
    ]

    # Drop each collection
    for collection_name in collections_to_drop:
        try:
            await db[collection_name].drop()
            print(f"✅ Dropped collection: {collection_name}")
        except Exception as e:
            print(f"⚠️ Collection {collection_name} doesn't exist or error: {e}")

    print("🔧 Creating fresh indexes...")

    # Create indexes for better performance
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("mobile", unique=True)
        await db.users.create_index("status")
        await db.users.create_index("role")

        # Groups collection indexes
        await db.groups.create_index("group_name", unique=True)
        await db.groups.create_index("api_key", unique=True)
        await db.groups.create_index("created_by")
        await db.groups.create_index("trading_status")

        # Members collection indexes
        await db.members.create_index([("user_id", 1), ("group_id", 1)], unique=True)
        await db.members.create_index("group_id")
        await db.members.create_index("user_id")
        await db.members.create_index("status")

        # Trading accounts indexes
        await db.trading_accounts.create_index("user_id")
        await db.trading_accounts.create_index("account_number", unique=True)
        await db.trading_accounts.create_index("broker")
        await db.trading_accounts.create_index("status")

        # Settlements collection indexes
        await db.settlements.create_index("group_id")
        await db.settlements.create_index("submitted_by")
        await db.settlements.create_index("status")
        await db.settlements.create_index("settlement_period_start")

        # Trades collection indexes
        await db.trades.create_index("master_account_id")
        await db.trades.create_index("slave_account_id")
        await db.trades.create_index("group_id")
        await db.trades.create_index("symbol")
        await db.trades.create_index("open_time")
        await db.trades.create_index("status")

        # Master accounts indexes
        await db.master_accounts.create_index("account_id", unique=True)
        await db.master_accounts.create_index("group_id")
        await db.master_accounts.create_index("health_status")

        # Error logs indexes
        await db.error_logs.create_index("timestamp")
        await db.error_logs.create_index("member_id")
        await db.error_logs.create_index("group_id")
        await db.error_logs.create_index("reason_code")

        # OTP records indexes
        await db.otp_records.create_index("mobile_or_email")
        await db.otp_records.create_index("expires_at")
        await db.otp_records.create_index("status")
        await db.otp_records.create_index("otp_type")

        # Symbol mappings indexes
        await db.symbol_mappings.create_index([("master_symbol", 1), ("master_broker", 1), ("follower_broker", 1)], unique=True)
        await db.symbol_mappings.create_index("master_broker")
        await db.symbol_mappings.create_index("follower_broker")

        # Audit logs indexes
        await db.audit_logs.create_index("user_id")
        await db.audit_logs.create_index("timestamp")
        await db.audit_logs.create_index("action")
        await db.audit_logs.create_index("entity_type")

        print("✅ All indexes created successfully")

    except Exception as e:
        print(f"⚠️ Error creating indexes: {e}")

async def create_admin_user():
    """Create default admin user"""
    print("👤 Creating default admin user...")

    admin_data = {
        "name": "System Administrator",
        "mobile": "+918888888888",
        "email": "admin@4xengineer.com",
        "country": "India",
        "state": "Maharashtra",
        "city": "Mumbai",
        "pin_code": "400001",
        "password": "Admin@123456",
        "role": "admin"
    }

    result = await mongodb_service.create_user(admin_data)

    if result["status"]:
        print(f"✅ Admin user created: {admin_data['email']}")

        # Activate admin user
        db = mongodb_service.get_db()
        if db is not None:
            await db.users.update_one(
                {"email": admin_data['email']},
                {"$set": {
                    "status": "active",
                    "role": "admin",
                    "mobile_verified": True,
                    "email_verified": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }}
            )
            print("✅ Admin user activated")
        return result["data"]["user_id"]
    else:
        print(f"❌ Failed to create admin: {result['message']}")
        return None

async def create_sample_users():
    """Create sample users for testing"""
    print("👥 Creating sample users...")

    sample_users = [
        {
            "name": "John Trader",
            "mobile": "+919876543210",
            "email": "trader@4xengineer.com",
            "country": "India",
            "state": "Karnataka",
            "city": "Bangalore",
            "pin_code": "560001",
            "password": "Trader@123456",
            "role": "user"
        },
        {
            "name": "Master Expert",
            "mobile": "+917777777777",
            "email": "master@4xengineer.com",
            "country": "India",
            "state": "Delhi",
            "city": "New Delhi",
            "pin_code": "110001",
            "password": "Master@123456",
            "role": "master"
        },
        {
            "name": "Group Manager",
            "mobile": "+916666666666",
            "email": "manager@4xengineer.com",
            "country": "India",
            "state": "Tamil Nadu",
            "city": "Chennai",
            "pin_code": "600001",
            "password": "Manager@123456",
            "role": "group_manager"
        }
    ]

    created_users = []

    for user_data in sample_users:
        result = await mongodb_service.create_user(user_data)

        if result["status"]:
            print(f"✅ User created: {user_data['email']}")

            # Activate user
            db = mongodb_service.get_db()
            if db is not None:
                await db.users.update_one(
                    {"email": user_data['email']},
                    {"$set": {
                        "status": "active",
                        "role": user_data["role"],
                        "mobile_verified": True,
                        "email_verified": True,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }}
                )
                print(f"✅ User activated: {user_data['email']}")
                created_users.append(result["data"]["user_id"])
        else:
            print(f"❌ Failed to create user {user_data['email']}: {result['message']}")

    return created_users

async def create_sample_groups(admin_id, user_ids):
    """Create sample trading groups"""
    print("🏢 Creating sample trading groups...")

    if not admin_id or not user_ids:
        print("⚠️ Cannot create groups without admin and users")
        return

    db = mongodb_service.get_db()
    if db is None:
        print("❌ Database not available")
        return

    sample_groups = [
        {
            "group_name": "Elite Traders Group",
            "company_name": "4X Engineer Elite",
            "profit_sharing_percentage": 80,
            "settlement_cycle": "weekly",
            "grace_days": 2,
            "master_accounts": [],
            "api_key": f"mt5_api_elite_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "trading_status": "active",
            "created_by": admin_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_members": 0,
            "active_members": 0,
            "total_equity": 0.0,
            "total_profit": 0.0,
            "pending_settlement": 0.0
        },
        {
            "group_name": "Professional Copy Traders",
            "company_name": "4X Engineer Pro",
            "profit_sharing_percentage": 70,
            "settlement_cycle": "monthly",
            "grace_days": 3,
            "master_accounts": [],
            "api_key": f"mt5_api_pro_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "trading_status": "active",
            "created_by": admin_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_members": 0,
            "active_members": 0,
            "total_equity": 0.0,
            "total_profit": 0.0,
            "pending_settlement": 0.0
        }
    ]

    created_groups = []

    for group_data in sample_groups:
        try:
            result = await db.groups.insert_one(group_data)
            group_id = str(result.inserted_id)
            created_groups.append(group_id)
            print(f"✅ Group created: {group_data['group_name']} (ID: {group_id})")
        except Exception as e:
            print(f"❌ Failed to create group {group_data['group_name']}: {e}")

    return created_groups

async def main():
    """Main cleanup and setup function"""
    print("🚀 Starting clean database setup for MT5 Copy Trading Platform")
    print("=" * 70)

    # Step 1: Clean database
    await clean_database()

    # Step 2: Create admin user
    admin_id = await create_admin_user()

    # Step 3: Create sample users
    user_ids = await create_sample_users()

    # Step 4: Create sample groups
    group_ids = await create_sample_groups(admin_id, user_ids)

    print("\n" + "=" * 70)
    print("🎉 Database setup complete!")
    print("\n📋 Login Credentials:")
    print("Admin: admin@4xengineer.com / Admin@123456")
    print("Trader: trader@4xengineer.com / Trader@123456")
    print("Master: master@4xengineer.com / Master@123456")
    print("Manager: manager@4xengineer.com / Manager@123456")

    print(f"\n📊 Created:")
    print(f"- {len([admin_id] + user_ids)} Users")
    print(f"- {len(group_ids)} Trading Groups")
    print(f"- All necessary database indexes")

    print("\n✅ System ready for testing!")

if __name__ == "__main__":
    asyncio.run(main())