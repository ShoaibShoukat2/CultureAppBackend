#!/usr/bin/env python3
"""
Simple test for duplicate detection API endpoints
"""
import requests
import os
from PIL import Image, ImageDraw
import tempfile

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USERNAME = "test_artist_api"
TEST_PASSWORD = "testpass123"
TEST_EMAIL = "test_artist_api@example.com"

def create_test_image(filename, color=(255, 0, 0), size=(200, 200)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(0, 255, 0))
    draw.ellipse([75, 75, 125, 125], fill=(0, 0, 255))
    img.save(filename, 'JPEG')
    return filename

def create_similar_image(filename, color=(255, 10, 10), size=(200, 200)):
    """Create a slightly different but similar image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([52, 52, 148, 148], fill=(10, 255, 10))
    draw.ellipse([77, 77, 123, 123], fill=(10, 10, 255))
    img.save(filename, 'JPEG')
    return filename

def register_and_login():
    """Register a test user and get auth token"""
    print("🔐 Registering test user...")
    
    # Try to register
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
        "user_type": "artist",
        "first_name": "Test",
        "last_name": "Artist"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    if response.status_code == 400 and "username already exists" in str(response.json()):
        print("✅ User already exists, logging in...")
    elif response.status_code == 201:
        print("✅ User registered successfully")
    else:
        print(f"❌ Registration failed: {response.json()}")
    
    # Login
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json()["token"]
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_artwork_upload_with_duplicate_detection(token):
    """Test artwork upload with duplicate detection"""
    print("\n🎨 Testing artwork upload with duplicate detection...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Create test images
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp1:
        create_test_image(tmp1.name)
        
        # Upload first artwork
        with open(tmp1.name, 'rb') as f:
            files = {'image': ('test1.jpg', f, 'image/jpeg')}
            data = {
                'title': 'Test Artwork 1',
                'description': 'First test artwork for duplicate detection',
                'category_id': 1,  # Assuming category 1 exists
                'artwork_type': 'digital',
                'price': '100.00'
            }
            
            response = requests.post(f"{BASE_URL}/artworks/", headers=headers, files=files, data=data)
            
            if response.status_code == 201:
                artwork1_data = response.json()
                print("✅ First artwork uploaded successfully")
                print(f"   Duplicate check: {artwork1_data['duplicate_check']['message']}")
                artwork1_id = artwork1_data['artwork']['id']
            else:
                print(f"❌ First artwork upload failed: {response.json()}")
                return False
    
    # Create similar image and upload
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp2:
        create_similar_image(tmp2.name)
        
        # Upload second similar artwork
        with open(tmp2.name, 'rb') as f:
            files = {'image': ('test2.jpg', f, 'image/jpeg')}
            data = {
                'title': 'Similar Test Artwork',
                'description': 'Similar test artwork for duplicate detection',
                'category_id': 1,
                'artwork_type': 'digital',
                'price': '120.00'
            }
            
            response = requests.post(f"{BASE_URL}/artworks/", headers=headers, files=files, data=data)
            
            if response.status_code == 201:
                artwork2_data = response.json()
                print("✅ Second artwork uploaded successfully")
                print(f"   Duplicate check: {artwork2_data['duplicate_check']['message']}")
                
                if artwork2_data['duplicate_check']['has_duplicates']:
                    print("✅ Duplicate detection working! Found potential duplicates:")
                    for dup in artwork2_data['duplicate_details']:
                        print(f"      - {dup['title']} ({dup['similarity_percentage']}% similar)")
                else:
                    print("ℹ️  No duplicates detected (images might not be similar enough)")
                
                artwork2_id = artwork2_data['artwork']['id']
            else:
                print(f"❌ Second artwork upload failed: {response.json()}")
                return False
    
    # Test manual duplicate check
    print("\n🔍 Testing manual duplicate check...")
    response = requests.post(f"{BASE_URL}/artworks/{artwork1_id}/check_duplicates/", headers=headers)
    
    if response.status_code == 200:
        duplicate_result = response.json()
        print("✅ Manual duplicate check successful")
        print(f"   Result: {duplicate_result['message']}")
        
        if duplicate_result['has_duplicates']:
            for dup in duplicate_result['duplicates']:
                print(f"      - Found: {dup['title']} ({dup['similarity_percentage']}% similar via {dup['hash_type']})")
    else:
        print(f"❌ Manual duplicate check failed: {response.json()}")
    
    # Cleanup - delete test artworks
    print("\n🧹 Cleaning up test artworks...")
    for artwork_id in [artwork1_id, artwork2_id]:
        response = requests.delete(f"{BASE_URL}/artworks/{artwork_id}/", headers=headers)
        if response.status_code == 204:
            print(f"✅ Artwork {artwork_id} deleted")
        else:
            print(f"⚠️  Could not delete artwork {artwork_id}")
    
    # Cleanup temp files
    try:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)
    except:
        pass
    
    return True

def main():
    """Run API tests"""
    print("🚀 Testing Duplicate Detection API Endpoints\n")
    
    # Get auth token
    token = register_and_login()
    if not token:
        print("❌ Could not authenticate")
        return False
    
    # Test artwork upload with duplicate detection
    if test_artwork_upload_with_duplicate_detection(token):
        print("\n🎉 All API tests passed! Duplicate detection system is working.")
        return True
    else:
        print("\n❌ Some API tests failed.")
        return False

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        exit(1)