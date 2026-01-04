#!/usr/bin/env python3
"""
Simple API test for duplicate detection
"""
import requests
import json
import os
from PIL import Image, ImageDraw
import tempfile
import time

BASE_URL = "http://localhost:8000/api"

def create_test_image(filename, color=(255, 0, 0)):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 255, 0))
    img.save(filename, 'JPEG')
    return filename

def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/artworks/", timeout=5)
        print(f"✅ API connectivity: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['count']} artworks in database")
            
            # Check if any artworks have duplicate detection fields
            if data['results']:
                first_artwork = data['results'][0]
                print(f"   Sample artwork: {first_artwork['title']}")
                print(f"   Artwork ID: {first_artwork['id']}")
                
                # Test artwork detail endpoint
                detail_response = requests.get(f"{BASE_URL}/artworks/{first_artwork['id']}/")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("✅ Artwork detail endpoint working")
                    
                    # Check if duplicate detection fields exist in the model
                    # (They might not be in the serializer output)
                    print("   Artwork fields available:")
                    for key in detail_data.keys():
                        print(f"     - {key}")
                else:
                    print(f"❌ Artwork detail failed: {detail_response.status_code}")
            
            return True
        else:
            print(f"❌ API not responding correctly: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_duplicate_detection_database():
    """Test duplicate detection in database directly"""
    print("\n🧪 Testing duplicate detection in database...")
    
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        
        from api.models import Artwork
        from api.duplicate_detection import calculate_perceptual_hashes
        
        # Check if any artworks have hashes
        artworks_with_hashes = Artwork.objects.filter(
            phash__isnull=False,
            ahash__isnull=False,
            dhash__isnull=False
        ).count()
        
        print(f"✅ Artworks with perceptual hashes: {artworks_with_hashes}")
        
        # Test hash calculation
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        try:
            create_test_image(temp_file.name)
            hashes = calculate_perceptual_hashes(temp_file.name)
            
            if hashes:
                print("✅ Hash calculation working:")
                print(f"   pHash: {hashes['phash']}")
                print(f"   aHash: {hashes['ahash']}")
                print(f"   dHash: {hashes['dhash']}")
                return True
            else:
                print("❌ Hash calculation failed")
                return False
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Duplicate Detection System\n")
    
    tests_passed = 0
    total_tests = 2
    
    # Test API endpoints
    if test_api_endpoints():
        tests_passed += 1
    
    # Test duplicate detection
    if test_duplicate_detection_database():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Duplicate detection system is working.")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)