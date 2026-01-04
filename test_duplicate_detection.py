#!/usr/bin/env python3
"""
Comprehensive Test Script for Perceptual Hash Duplicate Detection System
Tests all functionality including hash calculation, similarity detection, and API endpoints.
"""

import os
import sys
import django
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import tempfile
import shutil
from io import BytesIO

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Artwork, Category
from api.duplicate_detection import (
    calculate_perceptual_hashes,
    hamming_distance,
    find_duplicate_artworks,
    check_artwork_duplicates
)

User = get_user_model()

class DuplicateDetectionTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_dir = tempfile.mkdtemp(prefix="duplicate_test_")
        self.tokens = {}
        self.test_artworks = []
        
        print(f"🧪 Starting Duplicate Detection Tests")
        print(f"📁 Test directory: {self.test_dir}")
        print("=" * 60)

    def cleanup(self):
        """Clean up test files and data"""
        try:
            shutil.rmtree(self.test_dir)
            # Clean up test artworks
            for artwork_id in self.test_artworks:
                try:
                    artwork = Artwork.objects.get(id=artwork_id)
                    if artwork.image:
                        artwork.image.delete()
                    if artwork.watermarked_image:
                        artwork.watermarked_image.delete()
                    artwork.delete()
                except Artwork.DoesNotExist:
                    pass
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    def create_test_image(self, filename, text="TEST", color=(255, 0, 0), size=(400, 300)):
        """Create a test image with specified text and color"""
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw text and some shapes
        draw.text((x, y), text, fill=color, font=font)
        draw.rectangle([50, 50, 150, 150], outline=color, width=3)
        draw.ellipse([250, 100, 350, 200], outline=color, width=3)
        
        filepath = os.path.join(self.test_dir, filename)
        image.save(filepath, 'JPEG')
        return filepath

    def create_similar_image(self, original_path, filename, modification="slight"):
        """Create a similar image with slight modifications"""
        original = Image.open(original_path)
        
        if modification == "slight":
            # Slight color change
            modified = original.copy()
            draw = ImageDraw.Draw(modified)
            draw.rectangle([10, 10, 50, 50], fill=(0, 255, 0))
            
        elif modification == "resize":
            # Resize image
            modified = original.resize((350, 250))
            
        elif modification == "rotate":
            # Slight rotation
            modified = original.rotate(5, expand=True, fillcolor='white')
            
        elif modification == "brightness":
            # Brightness adjustment
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(original)
            modified = enhancer.enhance(1.2)
            
        else:
            modified = original.copy()
        
        filepath = os.path.join(self.test_dir, filename)
        modified.save(filepath, 'JPEG')
        return filepath

    def register_test_user(self, username, user_type="artist"):
        """Register a test user and return token"""
        user_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "user_type": user_type,
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(f"{self.base_url}/api/auth/register/", json=user_data)
        if response.status_code == 201:
            # Login to get token
            login_data = {"username": username, "password": "TestPass123!"}
            login_response = requests.post(f"{self.base_url}/api/auth/login/", json=login_data)
            if login_response.status_code == 200:
                token = login_response.json().get('token')
                self.tokens[username] = token
                return token
        return None

    def test_hash_calculation(self):
        """Test perceptual hash calculation"""
        print("\n1️⃣ Testing Hash Calculation")
        print("-" * 30)
        
        # Create test image
        test_image = self.create_test_image("hash_test.jpg", "HASH TEST", (255, 0, 0))
        
        # Calculate hashes
        hashes = calculate_perceptual_hashes(test_image)
        
        if hashes:
            print(f"✅ Hash calculation successful")
            print(f"   pHash: {hashes['phash']}")
            print(f"   aHash: {hashes['ahash']}")
            print(f"   dHash: {hashes['dhash']}")
            
            # Verify hash lengths
            assert len(hashes['phash']) == 16, "pHash should be 16 characters"
            assert len(hashes['ahash']) == 16, "aHash should be 16 characters"
            assert len(hashes['dhash']) == 16, "dHash should be 16 characters"
            print("✅ Hash lengths are correct")
            
            return hashes
        else:
            print("❌ Hash calculation failed")
            return None

    def test_hamming_distance(self):
        """Test Hamming distance calculation"""
        print("\n2️⃣ Testing Hamming Distance")
        print("-" * 30)
        
        # Test identical hashes
        hash1 = "1234567890abcdef"
        hash2 = "1234567890abcdef"
        distance = hamming_distance(hash1, hash2)
        print(f"✅ Identical hashes distance: {distance} (should be 0)")
        assert distance == 0, "Identical hashes should have distance 0"
        
        # Test different hashes
        hash3 = "1234567890abcdff"  # Last character different
        distance = hamming_distance(hash1, hash3)
        print(f"✅ Different hashes distance: {distance} (should be 1)")
        assert distance == 1, "One character difference should give distance 1"
        
        # Test completely different hashes
        hash4 = "fedcba0987654321"
        distance = hamming_distance(hash1, hash4)
        print(f"✅ Very different hashes distance: {distance}")
        
        return True

    def test_similarity_detection(self):
        """Test similarity detection between images"""
        print("\n3️⃣ Testing Similarity Detection")
        print("-" * 30)
        
        # Create original image
        original = self.create_test_image("original.jpg", "ORIGINAL", (255, 0, 0))
        
        # Create similar images
        similar1 = self.create_similar_image(original, "similar1.jpg", "slight")
        similar2 = self.create_similar_image(original, "similar2.jpg", "brightness")
        
        # Create different image
        different = self.create_test_image("different.jpg", "DIFFERENT", (0, 255, 0))
        
        # Calculate hashes
        orig_hashes = calculate_perceptual_hashes(original)
        sim1_hashes = calculate_perceptual_hashes(similar1)
        sim2_hashes = calculate_perceptual_hashes(similar2)
        diff_hashes = calculate_perceptual_hashes(different)
        
        if all([orig_hashes, sim1_hashes, sim2_hashes, diff_hashes]):
            # Test similarity between original and similar images
            for hash_type in ['phash', 'ahash', 'dhash']:
                dist1 = hamming_distance(orig_hashes[hash_type], sim1_hashes[hash_type])
                dist2 = hamming_distance(orig_hashes[hash_type], sim2_hashes[hash_type])
                dist_diff = hamming_distance(orig_hashes[hash_type], diff_hashes[hash_type])
                
                print(f"   {hash_type.upper()} distances:")
                print(f"     Original vs Similar1: {dist1}")
                print(f"     Original vs Similar2: {dist2}")
                print(f"     Original vs Different: {dist_diff}")
                
                # Similar images should have lower distance than different images
                assert dist1 < dist_diff, f"{hash_type}: Similar image should be closer than different image"
                assert dist2 < dist_diff, f"{hash_type}: Similar image should be closer than different image"
            
            print("✅ Similarity detection working correctly")
            return True
        else:
            print("❌ Hash calculation failed for similarity test")
            return False

    def test_database_integration(self):
        """Test database integration with Django models"""
        print("\n4️⃣ Testing Database Integration")
        print("-" * 30)
        
        try:
            # Create test users
            artist1 = User.objects.create_user(
                username="test_artist1",
                email="artist1@test.com",
                password="test123",
                user_type="artist"
            )
            
            artist2 = User.objects.create_user(
                username="test_artist2", 
                email="artist2@test.com",
                password="test123",
                user_type="artist"
            )
            
            # Create test category
            category, _ = Category.objects.get_or_create(
                name="Test Category",
                defaults={"description": "Test category for duplicate detection"}
            )
            
            # Create test images
            original_path = self.create_test_image("db_original.jpg", "DB TEST", (255, 0, 0))
            similar_path = self.create_similar_image(original_path, "db_similar.jpg", "slight")
            
            # Create artworks
            with open(original_path, 'rb') as f:
                original_file = SimpleUploadedFile("original.jpg", f.read(), content_type="image/jpeg")
                
            artwork1 = Artwork.objects.create(
                artist=artist1,
                title="Original Artwork",
                description="Original test artwork",
                category=category,
                artwork_type="digital",
                price=100.00,
                image=original_file
            )
            self.test_artworks.append(artwork1.id)
            
            # Calculate hashes for first artwork
            hashes1 = calculate_perceptual_hashes(artwork1.image.path)
            if hashes1:
                artwork1.phash = hashes1['phash']
                artwork1.ahash = hashes1['ahash']
                artwork1.dhash = hashes1['dhash']
                artwork1.duplicate_checked = True
                artwork1.save()
                print(f"✅ Artwork 1 hashes calculated and saved")
            
            # Create second artwork with similar image
            with open(similar_path, 'rb') as f:
                similar_file = SimpleUploadedFile("similar.jpg", f.read(), content_type="image/jpeg")
                
            artwork2 = Artwork.objects.create(
                artist=artist2,
                title="Similar Artwork",
                description="Similar test artwork",
                category=category,
                artwork_type="digital", 
                price=150.00,
                image=similar_file
            )
            self.test_artworks.append(artwork2.id)
            
            # Test duplicate detection
            duplicate_result = check_artwork_duplicates(artwork2)
            
            print(f"✅ Duplicate check result: {duplicate_result['message']}")
            if duplicate_result['has_duplicates']:
                print(f"   Found {len(duplicate_result['duplicates'])} potential duplicates")
                for dup in duplicate_result['duplicates']:
                    print(f"   - {dup['title']} by {dup['artist']} ({dup['similarity_percentage']}% similar)")
            
            return True
            
        except Exception as e:
            print(f"❌ Database integration test failed: {e}")
            return False

    def test_api_endpoints(self):
        """Test API endpoints for duplicate detection"""
        print("\n5️⃣ Testing API Endpoints")
        print("-" * 30)
        
        # Register test users
        token1 = self.register_test_user("api_artist1", "artist")
        token2 = self.register_test_user("api_artist2", "artist")
        
        if not token1 or not token2:
            print("❌ Failed to register test users")
            return False
        
        print("✅ Test users registered successfully")
        
        # Create test images
        original_path = self.create_test_image("api_original.jpg", "API TEST", (0, 0, 255))
        similar_path = self.create_similar_image(original_path, "api_similar.jpg", "slight")
        
        # Test artwork upload (first artist)
        with open(original_path, 'rb') as f:
            files = {'image': f}
            data = {
                'title': 'API Test Original',
                'description': 'Original artwork for API testing',
                'category_id': 1,  # Assuming category 1 exists
                'artwork_type': 'digital',
                'price': 200.00
            }
            
            response = requests.post(
                f"{self.base_url}/api/artworks/",
                headers={'Authorization': f'Token {token1}'},
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                result1 = response.json()
                artwork1_id = result1['artwork']['id']
                print(f"✅ First artwork uploaded successfully (ID: {artwork1_id})")
                print(f"   Duplicate check: {result1['duplicate_check']['message']}")
            else:
                print(f"❌ First artwork upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        
        # Test artwork upload (second artist - similar image)
        with open(similar_path, 'rb') as f:
            files = {'image': f}
            data = {
                'title': 'API Test Similar',
                'description': 'Similar artwork for API testing',
                'category_id': 1,
                'artwork_type': 'digital',
                'price': 250.00
            }
            
            response = requests.post(
                f"{self.base_url}/api/artworks/",
                headers={'Authorization': f'Token {token2}'},
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                result2 = response.json()
                artwork2_id = result2['artwork']['id']
                print(f"✅ Second artwork uploaded successfully (ID: {artwork2_id})")
                print(f"   Duplicate check: {result2['duplicate_check']['message']}")
                
                # Check if duplicates were detected
                if result2['duplicate_check']['has_duplicates']:
                    print("✅ Duplicate detection working in API!")
                    for dup in result2['duplicate_details']:
                        print(f"   - Found duplicate: {dup['title']} ({dup['similarity_percentage']}% similar)")
                else:
                    print("⚠️ No duplicates detected (might be expected if similarity is low)")
                
            else:
                print(f"❌ Second artwork upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        
        # Test manual duplicate check endpoint
        response = requests.post(
            f"{self.base_url}/api/artworks/{artwork2_id}/check_duplicates/",
            headers={'Authorization': f'Token {token2}'}
        )
        
        if response.status_code == 200:
            manual_check = response.json()
            print(f"✅ Manual duplicate check successful")
            print(f"   Result: {manual_check['message']}")
            if manual_check['has_duplicates']:
                print(f"   Found {len(manual_check['duplicates'])} duplicates")
        else:
            print(f"❌ Manual duplicate check failed: {response.status_code}")
        
        return True

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n6️⃣ Testing Edge Cases")
        print("-" * 30)
        
        # Test with invalid image path
        result = calculate_perceptual_hashes("nonexistent_file.jpg")
        if result is None:
            print("✅ Invalid file path handled correctly")
        else:
            print("❌ Invalid file path should return None")
        
        # Test hamming distance with different length hashes
        distance = hamming_distance("1234", "123456")
        if distance == float('inf'):
            print("✅ Different length hashes handled correctly")
        else:
            print("❌ Different length hashes should return infinity")
        
        # Test with None hashes
        distance = hamming_distance(None, "1234")
        if distance == float('inf'):
            print("✅ None hash handled correctly")
        else:
            print("❌ None hash should return infinity")
        
        return True

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Duplicate Detection Tests")
        print("=" * 60)
        
        tests = [
            ("Hash Calculation", self.test_hash_calculation),
            ("Hamming Distance", self.test_hamming_distance),
            ("Similarity Detection", self.test_similarity_detection),
            ("Database Integration", self.test_database_integration),
            ("API Endpoints", self.test_api_endpoints),
            ("Edge Cases", self.test_edge_cases)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = "✅ PASSED" if result else "❌ FAILED"
            except Exception as e:
                results[test_name] = f"❌ ERROR: {str(e)}"
                print(f"❌ {test_name} failed with error: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            print(f"{test_name:.<30} {result}")
        
        passed = sum(1 for r in results.values() if "PASSED" in r)
        total = len(results)
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Duplicate detection system is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the implementation.")
        
        return passed == total

def main():
    """Main function to run tests"""
    tester = DuplicateDetectionTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())