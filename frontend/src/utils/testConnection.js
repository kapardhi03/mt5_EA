// frontend/src/utils/testConnection.js
// Run this in browser console to test API connection

const testAPIConnection = async () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
    console.log('🔍 Testing API Connection...');
    
    try {
      // Test 1: Check if API is running
      console.log('\n1️⃣ Testing API Health...');
      const healthResponse = await fetch(`${API_BASE_URL}/api/docs`);
      console.log('✅ API Docs accessible:', healthResponse.ok);
      
      // Test 2: Try to register a test user
      console.log('\n2️⃣ Testing User Registration...');
      const registerData = {
        email: 'test@example.com',
        mobile: '+1234567890',
        password: 'test123',
        first_name: 'Test',
        last_name: 'User',
        role: 'member'
      };
      
      const registerResponse = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData)
      });
      
      const registerResult = await registerResponse.json();
      console.log('📝 Registration Response:', registerResult);
      
      // Test 3: Try to login with the test user
      if (registerResult.success) {
        console.log('\n3️⃣ Testing User Login...');
        const loginData = {
          mobile_or_email: 'test@example.com',
          password: 'test123'
        };
        
        const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loginData)
        });
        
        const loginResult = await loginResponse.json();
        console.log('🔐 Login Response:', loginResult);
        
        if (loginResult.success) {
          console.log('✅ Frontend-Backend connection is WORKING!');
          console.log('🎉 You can now use real database credentials in your frontend');
          
          // Test 4: Test authenticated endpoint
          console.log('\n4️⃣ Testing Authenticated Endpoint...');
          const token = loginResult.data.access_token;
          
          const dashboardResponse = await fetch(`${API_BASE_URL}/api/v1/users/dashboard`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            }
          });
          
          const dashboardResult = await dashboardResponse.json();
          console.log('📊 Dashboard Response:', dashboardResult);
          
        } else {
          console.log('❌ Login failed:', loginResult.message);
        }
      } else {
        console.log('❌ Registration failed:', registerResult.message);
        
        // Maybe user already exists, try login directly
        console.log('\n🔄 Trying direct login (user might exist)...');
        const loginData = {
          mobile_or_email: 'test@example.com',
          password: 'test123'
        };
        
        const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loginData)
        });
        
        const loginResult = await loginResponse.json();
        console.log('🔐 Direct Login Response:', loginResult);
      }
      
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      console.log('💡 Check if your backend is running at:', API_BASE_URL);
    }
  };
  
  // Export for use
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = testAPIConnection;
  } else {
    // Make available in browser console
    window.testAPIConnection = testAPIConnection;
    
    console.log(`
  🧪 API Connection Tester Loaded!
  
  Run this in your browser console:
  testAPIConnection()
  
  This will test:
  ✅ API accessibility  
  ✅ User registration
  ✅ User login
  ✅ Authenticated endpoints
    `);
  }