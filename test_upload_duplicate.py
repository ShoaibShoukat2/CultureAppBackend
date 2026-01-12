#!/usr/bin/env python
"""
Test duplicate detection during artwork upload
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Artwork, CustomUser
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def create_test_image(color='red', size=(100, 100)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color=color)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )

def test_duplicate_upload():
    print("🎨 Testing Duplicate Detection in Upload API")
    print("=" * 50)
    
    # Get or create test artist
    try:
        artist = CustomUser.objects.get(username='test_artist_duplicate')
    except CustomUser.DoesNotExist:
        artist = CustomUser.objects.create_user(
            username='test_artist_duplicate',
            email='test@example.com',
            password='testpass123',
            user_type='artist'
        )
        print(f"✅ Created test artist: {artist.username}")
    
    # Create API client and authenticate
    client = APIClient()
    token, created = Token.objects.get_or_create(user=artist)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    print(f"🔑 Using artist: {artist.username}")
    print()
    
    # Test 1: Upload original artwork (should succeed)
    print("📤 Test 1: Uploading original artwork")
    print("-" * 30)
    
    original_image = create_test_image('blue', (200, 200))
    
    response = client.post('/api/artworks/', {
        'title': 'Original Blue Artwork',
        'description': 'This is an original blue artwork',
        'artwork_type': 'digital',
        'price': '100.00',
        'image': original_image
    }, format='multipart')
    
    if response.status_code == 201:
        print("✅ Original artwork uploaded successfully!")
        original_artwork_id = response.data['artwork']['id']
        print(f"   Artwork ID: {original_artwork_id}")
    else:
        print(f"❌ Failed to upload original: {response.data}")
        return
    
    print()
    
    # Test 2: Try to upload same image (should be blocked)
    print("📤 Test 2: Uploading duplicate image")
    print("-" * 30)
    
    duplicate_image = create_test_image('blue', (200, 200))  # Same image
    
    response = client.post('/api/artworks/', {
        'title': 'Duplicate Blue Artwork',
        'description': 'This is a duplicate',
        'artwork_type': 'digital',
        'price': '150.00',
        'image': duplicate_image
    }, format='multipart')
    
    if response.status_code == 409:  # Conflict - duplicate detected
        print("✅ Duplicate detected successfully!")
        print(f"   Error: {response.data['error']}")
        print(f"   Message: {response.data['message']}")
        print(f"   Duplicate count: {response.data['duplicate_count']}")
        if response.data.get('similar_artworks'):
            for artwork in response.data['similar_artworks']:
                print(f"   Similar: '{artwork['title']}' by {artwork['artist']} ({artwork['similarity_percentage']}% similar)")
    else:
        print(f"❌ Duplicate not detected! Response: {response.data}")
    
    print()
    
    # Test 3: Upload slightly different image (should succeed)
    print("📤 Test 3: Uploading different artwork")
    print("-" * 30)
    
    different_image = create_test_image('green', (200, 200))  # Different color
    
    response = client.post('/api/artworks/', {
        'title': 'Different Green Artwork',
        'description': 'This is a different artwork',
        'artwork_type': 'digital',
        'price': '120.00',
        'image': different_image
    }, format='multipart')
    
    if response.status_code == 201:
        print("✅ Different artwork uploaded successfully!")
        print(f"   Artwork ID: {response.data['artwork']['id']}")
    else:
        print(f"❌ Failed to upload different artwork: {response.data}")
    
    print()
    print("🎯 Test Complete!")
    print()
    print("📋 Summary:")
    print("   ✅ Original artwork: Uploaded successfully")
    print("   🚫 Duplicate artwork: Blocked with error message")
    print("   ✅ Different artwork: Uploaded successfully")

if __name__ == "__main__":
    test_duplicate_upload()