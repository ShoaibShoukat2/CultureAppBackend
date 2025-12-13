#!/usr/bin/env python3
"""
Debug Job Creation Issue
"""

import requests
import json
import time

def test_job_creation():
    base_url = "http://127.0.0.1:8000"
    
    # First register a buyer
    buyer_data = {
        "username": f"debug_buyer_{int(time.time())}",
        "email": f"debug_buyer_{int(time.time())}@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Debug",
        "last_name": "Buyer",
        "user_type": "buyer"
    }
    
    print("🔍 Registering buyer...")
    response = requests.post(f"{base_url}/api/auth/register/", json=buyer_data)
    print(f"Registration Status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"Registration failed: {response.text}")
        return
    
    data = response.json()
    token = data.get('token')
    print(f"✅ Buyer registered, token: {token[:20]}...")
    
    # Get categories
    print("\n🔍 Getting categories...")
    response = requests.get(f"{base_url}/api/categories/")
    categories = response.json()
    if isinstance(categories, dict) and 'results' in categories:
        categories = categories['results']
    
    category_id = categories[0]['id'] if categories else None
    print(f"✅ Category ID: {category_id}")
    
    # Try to create job
    headers = {'Authorization': f'Token {token}'}
    job_data = {
        'title': 'Debug Test Project',
        'description': 'Testing job creation debugging',
        'budget_min': '50.00',
        'budget_max': '150.00',
        'duration_days': 7,
        'required_skills': 'Debug Testing',
        'experience_level': 'intermediate'
    }
    
    if category_id:
        job_data['category'] = category_id
    
    print(f"\n🔍 Creating job with data: {json.dumps(job_data, indent=2)}")
    print(f"Headers: {headers}")
    
    response = requests.post(f"{base_url}/api/jobs/", json=job_data, headers=headers)
    print(f"Job Creation Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Job created successfully!")
    else:
        print("❌ Job creation failed")
        
        # Try to get more details
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")

if __name__ == "__main__":
    test_job_creation()