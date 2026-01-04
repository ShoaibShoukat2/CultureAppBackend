#!/usr/bin/env python3
"""
Test script for the perceptual hash duplicate detection system
"""
import os
import sys
import django
from PIL import Image, ImageDraw
import tempfile
import shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Artwork, Category
from api.duplicate_detection import (
    calculate_perceptual_hashes,
    hamming_distance,
    find_duplicate_artworks,
    check_artwork_duplicates
)

User = get_user_model()

def create_test_image(filename, color=(255, 0, 0), size=(200, 200)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    # Add some pattern to make it more interesting
    draw.rectangle([50, 50, 150, 150], fill=(0, 255, 0))
    draw.ellipse([75, 75, 125, 125], fill=(0, 0, 255))
    img.save(filename)
    return filename

def create_similar_image(filename, color=(255, 10, 10), size=(200, 200)):
    """Create a slightly different but similar image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    # Similar pattern but slightly different
    draw.rectangle([52, 52, 148, 148], fill=(10, 255, 10))
    draw.ellipse([77, 77, 123, 123], fill=(10, 10, 255))
    img.save(filename)
    return filename

def create_different_image(filename, color=(0, 255, 255), size=(200, 200)):
    """Create a completely different image"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    # Completely different pattern
    for i in range(0, 200, 20):
        draw.line([(i, 0), (i, 200)], fill=(255, 0, 255), width=2)
        draw.line([(0, i), (200, i)], fill=(255, 255, 0), width=2)
    img.save(filename)
    return filename

def test_hash_calculation():
    """Test perceptual hash calculation"""
    print("🧪 Testing hash calculation...")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        create_test_image(tmp.name)
        
        hashes = calculate_perceptual_hashes(tmp.name)
        
        if hashes:
            print(f"✅ Hash calculation successful:")
            print(f"   pHash: {hashes['phash']}")
            print(f"   aHash: {hashes['ahash']}")
            print(f"   dHash: {hashes['dhash']}")
            
            # Verify hash lengths
            assert len(hashes['phash']) == 16, f"pHash should be 16 chars, got {len(hashes['phash'])}"
            assert len(hashes['ahash']) == 16, f"aHash should be 16 chars, got {len(hashes['ahash'])}"
            assert len(hashes['dhash']) == 16, f"dHash should be 16 chars, got {len(hashes['dhash'])}"
            
            print("✅ Hash lengths are correct")
        else:
            print("❌ Hash calculation failed")
            return False
        
        os.unlink(tmp.name)
    
    return True

def test_hamming_distance():
    """Test Hamming distance calculation"""
    print("\n🧪 Testing Hamming distance...")
    
    # Test identical hashes
    hash1 = "1234567890abcdef"
    hash2 = "1234567890abcdef"
    distance = hamming_distance(hash1, hash2)
    print(f"✅ Identical hashes distance: {distance} (should be 0)")
    assert distance == 0
    
    # Test completely different hashes
    hash1 = "0000000000000000"
    hash2 = "ffffffffffffffff"
    distance = hamming_distance(hash1, hash2)
    print(f"✅ Different hashes distance: {distance} (should be 64)")
    assert distance == 64
    
    # Test partially different hashes
    hash1 = "1234567890abcdef"
    hash2 = "1234567890abcdff"  # Last character different
    distance = hamming_distance(hash1, hash2)
    print(f"✅ Partially different hashes distance: {distance}")
    
    return True

def test_duplicate_detection_with_database():
    """Test duplicate detection with actual database records"""
    print("\n🧪 Testing duplicate detection with database...")
    
    # Create test users
    try:
        artist1 = User.objects.get(username='test_artist1')
    except User.DoesNotExist:
        artist1 = User.objects.create_user(
            username='test_artist1',
            email='artist1@test.com',
            password='testpass123',
            user_type='artist'
        )
    
    try:
        artist2 = User.objects.get(username='test_artist2')
    except User.DoesNotExist:
        artist2 = User.objects.create_user(
            username='test_artist2',
            email='artist2@test.com',
            password='testpass123',
            user_type='artist'
        )
    
    # Create test category
    category, _ = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for duplicate detection'}
    )
    
    # Create temporary directory for test images
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test images
        img1_path = os.path.join(temp_dir, 'test1.jpg')
        img2_path = os.path.join(temp_dir, 'similar.jpg')
        img3_path = os.path.join(temp_dir, 'different.jpg')
        
        create_test_image(img1_path)
        create_similar_image(img2_path)
        create_different_image(img3_path)
        
        # Create artworks
        with open(img1_path, 'rb') as f:
            artwork1 = Artwork.objects.create(
                artist=artist1,
                title='Test Artwork 1',
                description='First test artwork',
                category=category,
                artwork_type='digital',
                price=100.00
            )
            artwork1.image.save('test1.jpg', f, save=True)
        
        with open(img2_path, 'rb') as f:
            artwork2 = Artwork.objects.create(
                artist=artist2,
                title='Similar Artwork',
                description='Similar test artwork',
                category=category,
                artwork_type='digital',
                price=150.00
            )
            artwork2.image.save('similar.jpg', f, save=True)
        
        with open(img3_path, 'rb') as f:
            artwork3 = Artwork.objects.create(
                artist=artist2,
                title='Different Artwork',
                description='Different test artwork',
                category=category,
                artwork_type='digital',
                price=200.00
            )
            artwork3.image.save('different.jpg', f, save=True)
        
        # Test duplicate detection
        print("Testing artwork1 vs similar artwork...")
        result1 = check_artwork_duplicates(artwork1)
        print(f"✅ Artwork1 duplicate check: {result1['message']}")
        if result1['has_duplicates']:
            for dup in result1['duplicates']:
                print(f"   - Found duplicate: {dup['title']} by {dup['artist']} ({dup['similarity_percentage']}% similar)")
        
        print("Testing artwork2 vs different artwork...")
        result2 = check_artwork_duplicates(artwork2)
        print(f"✅ Artwork2 duplicate check: {result2['message']}")
        if result2['has_duplicates']:
            for dup in result2['duplicates']:
                print(f"   - Found duplicate: {dup['title']} by {dup['artist']} ({dup['similarity_percentage']}% similar)")
        
        print("Testing artwork3...")
        result3 = check_artwork_duplicates(artwork3)
        print(f"✅ Artwork3 duplicate check: {result3['message']}")
        if result3['has_duplicates']:
            for dup in result3['duplicates']:
                print(f"   - Found duplicate: {dup['title']} by {dup['artist']} ({dup['similarity_percentage']}% similar)")
        
        # Cleanup test artworks
        artwork1.delete()
        artwork2.delete()
        artwork3.delete()
        
        print("✅ Database duplicate detection test completed")
        
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)
    
    return True

def test_same_artist_exception():
    """Test that same artist can upload similar artworks"""
    print("\n🧪 Testing same artist exception...")
    
    try:
        artist = User.objects.get(username='test_same_artist')
    except User.DoesNotExist:
        artist = User.objects.create_user(
            username='test_same_artist',
            email='same_artist@test.com',
            password='testpass123',
            user_type='artist'
        )
    
    category, _ = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for duplicate detection'}
    )
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create two similar images
        img1_path = os.path.join(temp_dir, 'original.jpg')
        img2_path = os.path.join(temp_dir, 'variation.jpg')
        
        create_test_image(img1_path)
        create_similar_image(img2_path)
        
        # Create first artwork
        with open(img1_path, 'rb') as f:
            artwork1 = Artwork.objects.create(
                artist=artist,
                title='Original Artwork',
                description='Original artwork by same artist',
                category=category,
                artwork_type='digital',
                price=100.00
            )
            artwork1.image.save('original.jpg', f, save=True)
        
        # Create second similar artwork by same artist
        with open(img2_path, 'rb') as f:
            artwork2 = Artwork.objects.create(
                artist=artist,
                title='Artwork Variation',
                description='Variation by same artist',
                category=category,
                artwork_type='digital',
                price=120.00
            )
            artwork2.image.save('variation.jpg', f, save=True)
        
        # Test duplicate detection - should not find duplicates for same artist
        result = check_artwork_duplicates(artwork2)
        print(f"✅ Same artist duplicate check: {result['message']}")
        
        if result['has_duplicates']:
            print("❌ ERROR: Same artist artworks should not be flagged as duplicates!")
            return False
        else:
            print("✅ Same artist exception working correctly")
        
        # Cleanup
        artwork1.delete()
        artwork2.delete()
        
    finally:
        shutil.rmtree(temp_dir)
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Perceptual Hash Duplicate Detection Tests\n")
    
    tests = [
        test_hash_calculation,
        test_hamming_distance,
        test_duplicate_detection_with_database,
        test_same_artist_exception
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                failed += 1
                print("❌ FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED with error: {e}\n")
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Duplicate detection system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)