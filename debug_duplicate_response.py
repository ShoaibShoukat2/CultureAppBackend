#!/usr/bin/env python3
"""
Debug script to check duplicate detection response
"""
import os
import sys
import django
from PIL import Image, ImageDraw
import tempfile
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Artwork, Category
from api.views import ArtworkViewSet
from api.serializers import ArtworkSerializer
from api.duplicate_detection import check_artwork_duplicates
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token

User = get_user_model()

def create_test_image(filename, color=(255, 0, 0)):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 255, 0))
    img.save(filename, 'JPEG')
    return filename

def test_duplicate_response():
    """Test what response is actually returned"""
    print("🧪 Testing duplicate detection response...")
    
    # Create test user
    try:
        user = User.objects.get(username='debug_test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='debug_test_user',
            email='debug@test.com',
            password='testpass123',
            user_type='artist'
        )
    
    # Create test category
    category, _ = Category.objects.get_or_create(
        name='Debug Category',
        defaults={'description': 'Debug category'}
    )
    
    # Create first artwork
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp1:
        create_test_image(tmp1.name, (255, 0, 0))
        
        artwork1 = Artwork.objects.create(
            artist=user,
            title='Debug Original Artwork',
            description='Original artwork for debug',
            category=category,
            artwork_type='digital',
            price=100.00
        )
        
        with open(tmp1.name, 'rb') as f:
            artwork1.image.save('debug_original.jpg', f, save=True)
        
        # Check duplicate detection on first artwork
        result1 = check_artwork_duplicates(artwork1)
        print(f"✅ First artwork result: {json.dumps(result1, indent=2)}")
        
        # Check if hashes were calculated
        artwork1.refresh_from_db()
        print(f"📊 First artwork hashes:")
        print(f"   pHash: {artwork1.phash}")
        print(f"   aHash: {artwork1.ahash}")
        print(f"   dHash: {artwork1.dhash}")
        print(f"   Duplicate checked: {artwork1.duplicate_checked}")
    
    # Create second similar artwork
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp2:
        create_test_image(tmp2.name, (255, 5, 5))  # Very similar
        
        artwork2 = Artwork.objects.create(
            artist=user,  # Same artist - should not be flagged
            title='Debug Similar Artwork Same Artist',
            description='Similar artwork by same artist',
            category=category,
            artwork_type='digital',
            price=120.00
        )
        
        with open(tmp2.name, 'rb') as f:
            artwork2.image.save('debug_similar_same.jpg', f, save=True)
        
        result2 = check_artwork_duplicates(artwork2)
        print(f"\n✅ Second artwork (same artist) result: {json.dumps(result2, indent=2)}")
    
    # Create third artwork by different artist
    try:
        user2 = User.objects.get(username='debug_test_user2')
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username='debug_test_user2',
            email='debug2@test.com',
            password='testpass123',
            user_type='artist'
        )
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp3:
        create_test_image(tmp3.name, (255, 2, 2))  # Very similar to first
        
        artwork3 = Artwork.objects.create(
            artist=user2,  # Different artist - should be flagged
            title='Debug Similar Artwork Different Artist',
            description='Similar artwork by different artist',
            category=category,
            artwork_type='digital',
            price=130.00
        )
        
        with open(tmp3.name, 'rb') as f:
            artwork3.image.save('debug_similar_diff.jpg', f, save=True)
        
        result3 = check_artwork_duplicates(artwork3)
        print(f"\n✅ Third artwork (different artist) result: {json.dumps(result3, indent=2)}")
        
        # Check if this would be blocked
        if result3['has_duplicates']:
            for dup in result3['duplicates']:
                print(f"   🚨 Found duplicate: {dup['title']} ({dup['similarity_percentage']:.1f}% similar)")
                if dup['similarity_percentage'] >= 85.0:
                    print(f"   🚫 This would be BLOCKED (≥85% similar)")
                else:
                    print(f"   ⚠️  This would show WARNING (<85% similar)")
    
    # Test API response format
    print(f"\n📱 Testing API response format...")
    
    # Simulate API response for successful upload
    api_response = {
        'message': 'Artwork uploaded successfully',
        'artwork': ArtworkSerializer(artwork1).data,
        'duplicate_check': result1
    }
    
    if result1['has_duplicates']:
        api_response['warning'] = 'Some similar artworks found, but not similar enough to block upload.'
        api_response['duplicate_details'] = result1['duplicates']
    
    print(f"API Response Structure:")
    print(json.dumps(api_response, indent=2, default=str))
    
    # Cleanup
    try:
        artwork1.delete()
        artwork2.delete()
        artwork3.delete()
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)
        os.unlink(tmp3.name)
    except:
        pass
    
    return True

def main():
    """Run debug test"""
    print("🔍 Debugging Duplicate Detection Response\n")
    
    try:
        test_duplicate_response()
        print("\n✅ Debug test completed successfully!")
    except Exception as e:
        print(f"\n❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()