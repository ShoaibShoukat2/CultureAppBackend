#!/usr/bin/env python3
"""
Debug Bid Creation Issue
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_bid_creation():
    base_url = "http://127.0.0.1:8000"
    
    # Register artist
    artist_data = {
        "username": f"debug_artist_{int(time.time())}",
        "email": f"debug_artist_{int(time.time())}@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Debug",
        "last_name": "Artist",
        "user_type": "artist"
    }
    
    print("🔍 Registering artist...")
    response = requests.post(f"{base_url}/api/auth/register/", json=artist_data)
    artist_token = response.json().get('token')
    print(f"✅ Artist registered, token: {artist_token[:20]}...")
    
    # Register buyer
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
    buyer_token = response.json().get('token')
    print(f"✅ Buyer registered, token: {buyer_token[:20]}...")
    
    # Get categories
    response = requests.get(f"{base_url}/api/categories/")
    categories = response.json()
    if isinstance(categories, dict) and 'results' in categories:
        categories = categories['results']
    category_id = categories[0]['id'] if categories else None
    
    # Create job
    deadline = (datetime.now() + timedelta(days=14)).isoformat()
    job_data = {
        'title': 'Debug Job for Bidding',
        'description': 'Testing bid creation',
        'budget_min': '50.00',
        'budget_max': '150.00',
        'duration_days': 7,
        'required_skills': 'Debug Testing',
        'experience_level': 'intermediate',
        'deadline': deadline,
        'category': category_id
    }
    
    headers = {'Authorization': f'Token {buyer_token}'}
    print("🔍 Creating job...")
    response = requests.post(f"{base_url}/api/jobs/", json=job_data, headers=headers)
    job_id = response.json().get('id')
    print(f"✅ Job created, ID: {job_id}")
    
    # Try to create bid
    bid_data = {
        'job': job_id,
        'bid_amount': '100.00',
        'delivery_time': 5,
        'proposal': 'Debug bid proposal'
    }
    
    headers = {'Authorization': f'Token {artist_token}'}
    print(f"\n🔍 Creating bid with data: {json.dumps(bid_data, indent=2)}")
    
    response = requests.post(f"{base_url}/api/bids/", json=bid_data, headers=headers)
    print(f"Bid Creation Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Bid created successfully!")
    else:
        print("❌ Bid creation failed")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")

if __name__ == "__main__":
    test_bid_creation()