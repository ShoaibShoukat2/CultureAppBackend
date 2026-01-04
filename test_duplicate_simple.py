#!/usr/bin/env python3
"""
Simple test to verify duplicate detection is working
"""
import os
import sys
import django
from PIL import Image, ImageDraw
import tempfile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Artwork, Category
from api.duplicate_detection import calculate_perceptual_hashes, check_artwork_duplicates

User = get_user_model()

def create_test_image(filename, color=(255, 0, 0), size=(100, 100)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 255, 0))
    img.save(filename, 'JPEG')
    return filename

def test_basic_functionality():
    """Test basic duplicate detection functionality"""
    print("🧪 Testing basic duplicate detection functionality...")
    
    # Test hash calculation
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        create_test_image(tmp.name)
        
        hashes = calculate_perceptual_hashes(tmp.name)
        
        if hashes and all(len(h) == 16 for h in hashes.values()):
            print("✅ Hash calculation working correctly")
            print(f"   pHash: {hashes['phash']}")
            print(f"   aHash: {hashes['ahash']}")
            print(f"   dHash: {hashes['dhash']}")
        else:
            print("❌ Hash calculation failed")
            return False
        
        os.unlink(tmp.name)
    
    # Test with database
    print("\n🧪 Testing database integration...")
    
    # Create test category
    category, _ = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category'}
    )
    
    # Create test user
    try:
        user = User.objects.get(username='test_duplicate_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_duplicate_user',
            email='test@example.com',
            password='testpass123',
            user_type='artist'
        )
    
    # Create test artwork
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        create_test_image(tmp.name)
        
        artwork = Artwork.objects.create(
            artist=user,
            title='Test Artwork',
            description='Test artwork for duplicate detection',
            category=category,
            artwork_type='digital',
            price=100.00
        )
        
        # Save image to artwork
        with open(tmp.name, 'rb') as f:
            artwork.image.save('test.jpg', f, save=True)
        
        # Test duplicate detection
        result = check_artwork_duplicates(artwork)
        
        print(f"✅ Duplicate check result: {result['message']}")
        print(f"   Has duplicates: {result['has_duplicates']}")
        print(f"   Duplicate count: {len(result['duplicates'])}")
        
        # Check if hashes were calculated
        artwork.refresh_from_db()
        if artwork.phash and artwork.ahash and artwork.dhash:
            print("✅ Perceptual hashes saved to database")
            print(f"   pHash: {artwork.phash}")
            print(f"   aHash: {artwork.ahash}")
            print(f"   dHash: {artwork.dhash}")
            print(f"   Duplicate checked: {artwork.duplicate_checked}")
        else:
            print("❌ Perceptual hashes not saved to database")
            return False
        
        # Cleanup
        artwork.delete()
        os.unlink(tmp.name)
    
    print("✅ All basic tests passed!")
    return True

def main():
    """Run the test"""
    print("🚀 Testing Duplicate Detection System\n")
    
    try:
        if test_basic_functionality():
            print("\n🎉 Duplicate detection system is working correctly!")
            return True
        else:
            print("\n❌ Some tests failed.")
            return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)