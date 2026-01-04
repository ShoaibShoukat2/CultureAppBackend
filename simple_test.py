import requests
import json

# Test basic API connectivity
print("Testing API connectivity...")

try:
    # Test registration
    register_data = {
        "username": "simple_test_user",
        "email": "simple@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "artist",
        "first_name": "Simple",
        "last_name": "Test"
    }
    
    response = requests.post("http://localhost:8000/api/auth/register/", json=register_data)
    print(f"Registration status: {response.status_code}")
    print(f"Registration response: {response.text}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        if 'token' in data:
            token = data['token']
            print(f"✅ Got token: {token[:20]}...")
        else:
            print("❌ No token in registration response")
    
    # Test login
    login_data = {
        "username": "simple_test_user",
        "password": "testpass123"
    }
    
    response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")