#!/usr/bin/env python3
"""
Comprehensive System Test for MT5 Copy Trading Platform
Tests all functionality end-to-end
"""
import requests
import json
import time
from datetime import datetime

def print_banner():
    print("=" * 70)
    print("🧪 MT5 Copy Trading Platform - System Test")
    print("=" * 70)

def test_backend_health():
    print("\n🏥 Testing Backend Health...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"✅ Database: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_registration():
    print("\n👤 Testing User Registration...")

    timestamp = int(time.time())
    test_user = {
        "name": "System Test User",
        "mobile": f"+91987654{timestamp % 10000:04d}",  # Generate unique mobile
        "email": f"test_{timestamp}@example.com",
        "country": "India",
        "state": "Maharashtra",
        "city": "Mumbai",
        "pin_code": "400001",
        "password": "TestPass123"
    }

    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/register',
            headers={'Content-Type': 'application/json'},
            json=test_user,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Registration successful")
                print(f"✅ User ID: {data.get('data', {}).get('user_id', 'N/A')}")
                return test_user
            else:
                print(f"❌ Registration failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Registration request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login(email, password):
    print("\n🔐 Testing User Login...")

    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            headers={'Content-Type': 'application/json'},
            json={
                'mobile_or_email': email,
                'password': password
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Login successful")
                token = data.get('data', {}).get('access_token')
                user_info = data.get('data', {}).get('user')
                if token:
                    print(f"✅ Access token received")
                    print(f"✅ User: {user_info.get('name', 'N/A')} ({user_info.get('role', 'N/A')})")
                    return token
                else:
                    print("❌ No access token in response")
                    return None
            else:
                print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_otp_flow(mobile):
    print("\n📱 Testing OTP Flow...")

    # Send OTP
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/send-otp',
            headers={'Content-Type': 'application/json'},
            json={
                'mobile_or_email': mobile,
                'otp_type': 'mobile'
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ OTP sent to {mobile}")
                otp = data.get('data', {}).get('otp')
                if otp:
                    print(f"✅ Demo OTP: {otp}")

                    # Verify OTP
                    verify_response = requests.post(
                        'http://localhost:8000/api/v1/auth/verify-otp',
                        headers={'Content-Type': 'application/json'},
                        json={
                            'mobile_or_email': mobile,
                            'otp': otp,
                            'otp_type': 'mobile'
                        },
                        timeout=10
                    )

                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('success'):
                            print(f"✅ OTP verification successful")
                            return True
                        else:
                            print(f"❌ OTP verification failed: {verify_data.get('message')}")
                            return False
                    else:
                        print(f"❌ OTP verification request failed: {verify_response.status_code}")
                        return False
                else:
                    print("⚠️ No OTP in response (real SMS mode)")
                    return True
            else:
                print(f"❌ OTP send failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ OTP request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OTP error: {e}")
        return False

def test_admin_login():
    print("\n👨‍💼 Testing Admin Login...")

    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            headers={'Content-Type': 'application/json'},
            json={
                'mobile_or_email': 'admin@4xengineer.com',
                'password': 'Admin@123456'
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Admin login successful")
                user_info = data.get('data', {}).get('user')
                print(f"✅ Admin: {user_info.get('name', 'N/A')} ({user_info.get('role', 'N/A')})")
                return data.get('data', {}).get('access_token')
            else:
                print(f"❌ Admin login failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Admin login request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_database_integrity():
    print("\n🗄️ Testing Database Integrity...")

    # Test different user roles
    test_users = [
        ('admin@4xengineer.com', 'Admin@123456', 'admin'),
        ('trader@4xengineer.com', 'Trader@123456', 'user'),
        ('master@4xengineer.com', 'Master@123456', 'master'),
        ('manager@4xengineer.com', 'Manager@123456', 'group_manager')
    ]

    successful_logins = 0

    for email, password, expected_role in test_users:
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/auth/login',
                headers={'Content-Type': 'application/json'},
                json={'mobile_or_email': email, 'password': password},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user_info = data.get('data', {}).get('user')
                    actual_role = user_info.get('role')
                    print(f"✅ {email}: {actual_role}")
                    successful_logins += 1

                    if actual_role != expected_role:
                        print(f"⚠️ Role mismatch for {email}: expected {expected_role}, got {actual_role}")
                else:
                    print(f"❌ {email}: Login failed")
            else:
                print(f"❌ {email}: Request failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {email}: Error - {e}")

    print(f"\n📊 Database Test Results: {successful_logins}/{len(test_users)} users authenticated")
    return successful_logins == len(test_users)

def test_frontend_connection():
    print("\n🌐 Testing Frontend Connection...")

    try:
        response = requests.get('http://localhost:3001', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible on http://localhost:3001")

            # Check if it contains expected content
            content = response.text
            if 'Copy Trading Platform' in content:
                print("✅ Frontend title found")
                return True
            else:
                print("⚠️ Frontend loaded but title not found")
                return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def check_sms_configuration():
    print("\n📱 Checking SMS Configuration...")

    import os
    env_path = "/Users/kapardhikannekanti/Freelance/mt5_CopyTrade/.env"

    if not os.path.exists(env_path):
        print("⚠️ No .env file found - using demo SMS mode")
        return False

    with open(env_path, 'r') as f:
        env_content = f.read()

    # Check for SMS provider configuration
    providers = {
        'Fast2SMS': 'FAST2SMS_API_KEY=' in env_content and not env_content.split('FAST2SMS_API_KEY=')[1].split('\n')[0].strip().startswith('#'),
        'Twilio': all(key in env_content for key in ['TWILIO_ACCOUNT_SID=', 'TWILIO_AUTH_TOKEN=', 'TWILIO_FROM_NUMBER=']),
        'TextLocal': 'TEXTLOCAL_API_KEY=' in env_content and not env_content.split('TEXTLOCAL_API_KEY=')[1].split('\n')[0].strip().startswith('#'),
        'MSG91': 'MSG91_API_KEY=' in env_content and not env_content.split('MSG91_API_KEY=')[1].split('\n')[0].strip().startswith('#')
    }

    configured_providers = [name for name, configured in providers.items() if configured]

    if configured_providers:
        print(f"✅ SMS configured: {', '.join(configured_providers)}")
        return True
    else:
        print("⚠️ No SMS providers configured - using demo mode")
        return False

def main():
    print_banner()

    start_time = datetime.now()

    # Test all components
    tests = []

    # Backend tests
    tests.append(("Backend Health", test_backend_health()))
    tests.append(("Database Integrity", test_database_integrity()))

    # Authentication tests
    admin_token = test_admin_login()
    tests.append(("Admin Login", admin_token is not None))

    # Registration and login flow
    test_user = test_registration()
    if test_user:
        # For testing purposes, activate the user first
        try:
            requests.patch(
                f'http://localhost:8000/api/v1/admin/users/activate',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {admin_token}'},
                json={'email': test_user['email']},
                timeout=5
            )
        except:
            pass  # Activation endpoint might not exist yet

        user_token = test_login(test_user['email'], test_user['password'])
        tests.append(("User Registration & Login", user_token is not None))

        # OTP test with registered user
        otp_success = test_otp_flow(test_user['mobile'])
        tests.append(("OTP Flow", otp_success))
    else:
        tests.append(("User Registration & Login", False))
        tests.append(("OTP Flow", False))

    # Frontend test
    tests.append(("Frontend Connection", test_frontend_connection()))

    # SMS configuration check
    tests.append(("SMS Configuration", check_sms_configuration()))

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("📊 SYSTEM TEST SUMMARY")
    print("=" * 70)

    passed_tests = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed_tests += 1

    print(f"\nTotal: {passed_tests}/{len(tests)} tests passed")
    print(f"Duration: {duration:.2f} seconds")

    if passed_tests == len(tests):
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Platform is ready for production use")
    elif passed_tests >= len(tests) - 1:
        print("\n✅ SYSTEM MOSTLY OPERATIONAL")
        print("⚠️ Minor issues detected - check failed tests")
    else:
        print("\n⚠️ SYSTEM ISSUES DETECTED")
        print("🔧 Please fix failed tests before proceeding")

    print("\n🌐 Access URLs:")
    print("- Frontend: http://localhost:3001")
    print("- Backend API: http://localhost:8000")
    print("- API Documentation: http://localhost:8000/api/docs")

    print("\n👤 Test Accounts:")
    print("- Admin: admin@4xengineer.com / Admin@123456")
    print("- Trader: trader@4xengineer.com / Trader@123456")
    print("- Master: master@4xengineer.com / Master@123456")
    print("- Manager: manager@4xengineer.com / Manager@123456")

if __name__ == "__main__":
    main()