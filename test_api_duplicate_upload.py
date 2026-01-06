#!/usr/bin/env python3
"""
Test API duplicate upload to see exact response
"""
import requests
import json
import os
from PIL import Image, ImageDraw
import tempfile

BASE_URL = "http://localhost:8000/api"

def create_test_image(filename, color=(255, 0, 0)):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 255, 0))
    img.save(filename, 'JPEG')
    return filename

def register_and_login(username, email):
    """Register and login user"""
    # Register
    register_data = {
        "username": username,
        "email": email,
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "artist",
        "first_name": "Test",
        "last_name": "Artist"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    if response.status_code == 400 and "username already exists" in str(response.json()):
        print(f"✅ User {username} already exists")
    elif response.status_code == 201:
        print(f"✅ User {username} registered successfully")
    
    # Login
    login_data = {
        "username": username,
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json()["token"]
        print(f"✅ User {username} logged in successfully")
        return token
    else:
        print(f"❌ Login failed for {username}: {response.json()}")
        return None

def upload_artwork(token, title, image_path):
    """Upload artwork and return full response"""
    headers = {"Authorization": f"Token {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'image': ('test.jpg', f, 'image/jpeg')}
        data = {
            'title': title,
            'description': f'Test artwork: {title}',
            'category_id': 1,
            'artwork_type': 'digital',
            'price': '100.00'
        }
        
        response = requests.post(f"{BASE_URL}/artworks/", headers=headers, files=files, data=data)
        
        print(f"\n📤 Upload Response for '{title}':")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Response Body:")
            print(json.dumps(response_data, indent=4))
            return response_data
        except:
            print(f"   Response Text: {response.text}")
            return None

def main():
    """Test duplicate upload via API"""
    print("🚀 Testing Duplicate Upload via API\n")
    
    # Get tokens for two different artists
    token1 = register_and_login("api_test_artist1", "artist1@apitest.com")
    token2 = register_and_login("api_test_artist2", "artist2@apitest.com")
    
    if not token1 or not token2:
        print("❌ Failed to get authentication tokens")
        return
    
    # Create test images
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp1:
        create_test_image(tmp1.name, (255, 0, 0))
        
        # Upload first artwork (original)
        print("=" * 60)
        result1 = upload_artwork(token1, "API Test Original", tmp1.name)
        
        if result1 and result1.get('artwork'):
            artwork1_id = result1['artwork']['id']
            print(f"✅ First artwork uploaded with ID: {artwork1_id}")
        
        # Upload second artwork (identical by different artist)
        print("=" * 60)
        result2 = upload_artwork(token2, "API Test Duplicate", tmp1.name)
        
        if result2:
            if result2.get('error'):
                print(f"🚫 Second upload BLOCKED: {result2['message']}")
            elif result2.get('artwork'):
                print(f"✅ Second artwork uploaded (allowed)")
                if result2.get('duplicate_check', {}).get('has_duplicates'):
                    print(f"⚠️  Duplicate warning shown")
        
        # Cleanup
        os.unlink(tmp1.name)
    
    # Create different image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp2:
        create_test_image(tmp2.name, (0, 255, 255))  # Different colors
        
        # Upload third artwork (different)
        print("=" * 60)
        result3 = upload_artwork(token2, "API Test Different", tmp2.name)
        
        if result3 and result3.get('artwork'):
            print(f"✅ Third artwork uploaded (different image)")
        
        # Cleanup
        os.unlink(tmp2.name)

if __name__ == '__main__':
    main()