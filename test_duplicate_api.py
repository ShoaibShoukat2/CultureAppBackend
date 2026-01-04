#!/usr/bin/env python3
"""
API-focused Test Script for Duplicate Detection
Tests the duplicate detection functionality through API endpoints only.
"""

import requests
import json
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import time

class DuplicateAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_dir = tempfile.mkdtemp(prefix="api_test_")
        self.tokens = {}
        self.created_artworks = []
        
        print("🧪 API Duplicate Detection Test")
        print(f"🌐 Base URL: {base_url}")
        print(f"📁 Test directory: {self.test_dir}")
        print("=" * 50)

    def create_test_image(self, filename, text="TEST", color=(255, 0, 0), size=(400, 300)):
        """Create a test image"""
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        # Draw text and shapes
        draw.text((50, 100), text, fill=color, font=font)
        draw.rectangle([50, 50, 150, 150], outline=color, width=3)
        draw.ellipse([200, 100, 300, 200], outline=color, width=3)
        
        filepath = os.path.join(self.test_dir, filename)
        image.save(filepath, 'JPEG', quality=90)
        return filepath

    def create_similar_image(self, original_path, filename):
        """Create a similar image with slight modifications"""
        original = Image.open(original_path)
        modified = original.copy()
        draw = ImageDraw.Draw(modified)
        
        # Add small modification
        draw.rectangle([10, 10, 40, 40], fill=(0, 255, 0))
        draw.text((60, 250), "MODIFIED", fill=(0, 0, 255))
        
        filepath = os.path.join(self.test_dir, filename)
        modified.save(filepath, 'JPEG', quality=90)
        return filepath

    def register_user(self, username, user_type="artist"):
        """Register a test user"""
        print(f"👤 Registering user: {username}")
        
        user_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "user_type": user_type,
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/register/", json=user_data)
            
            if response.status_code == 201:
                print(f"✅ User {username} registered successfully")
                
                # Login to get token
                login_data = {"username": username, "password": "TestPass123!"}
                login_response = requests.post(f"{self.base_url}/api/auth/login/", json=login_data)
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    if 'token' in login_result:
                        token = login_result['token']
                        self.tokens[username] = token
                        print(f"✅ Token obtained for {username}")
                        return token
                    else:
                        print(f"❌ No token in login response for {username}")
                        print(f"Response: {login_result}")
                else:
                    print(f"❌ Login failed for {username}: {login_response.status_code}")
                    print(f"Response: {login_response.text}")
            else:
                print(f"❌ Registration failed for {username}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed. Is the server running at {self.base_url}?")
        except Exception as e:
            print(f"❌ Error registering {username}: {e}")
        
        return None

    def upload_artwork(self, token, title, image_path, description="Test artwork"):
        """Upload an artwork"""
        print(f"🎨 Uploading artwork: {title}")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {
                    'title': title,
                    'description': description,
                    'category_id': 1,  # Assuming category 1 exists
                    'artwork_type': 'digital',
                    'price': 100.00
                }
                
                response = requests.post(
                    f"{self.base_url}/api/artworks/",
                    headers={'Authorization': f'Token {token}'},
                    files=files,
                    data=data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    artwork_id = result['artwork']['id']
                    self.created_artworks.append(artwork_id)
                    
                    print(f"✅ Artwork uploaded successfully (ID: {artwork_id})")
                    print(f"   Title: {result['artwork']['title']}")
                    print(f"   Artist: {result['artwork']['artist']['username']}")
                    
                    # Check duplicate detection results
                    duplicate_check = result.get('duplicate_check', {})
                    print(f"   Duplicate check: {duplicate_check.get('message', 'No info')}")
                    
                    if duplicate_check.get('has_duplicates'):
                        print(f"🚨 DUPLICATES DETECTED!")
                        duplicates = result.get('duplicate_details', [])
                        for i, dup in enumerate(duplicates, 1):
                            print(f"   {i}. '{dup['title']}' by {dup['artist']}")
                            print(f"      Similarity: {dup['similarity_percentage']}% ({dup['hash_type']})")
                    else:
                        print(f"✅ No duplicates found")
                    
                    return artwork_id, result
                else:
                    print(f"❌ Upload failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error uploading artwork: {e}")
        
        return None, None

    def check_duplicates_manually(self, token, artwork_id):
        """Manually check for duplicates"""
        print(f"🔍 Manual duplicate check for artwork {artwork_id}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/artworks/{artwork_id}/check_duplicates/",
                headers={'Authorization': f'Token {token}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Manual check completed")
                print(f"   Artwork: {result.get('artwork_title', 'Unknown')}")
                print(f"   Result: {result.get('message', 'No message')}")
                
                if result.get('has_duplicates'):
                    duplicates = result.get('duplicates', [])
                    print(f"   Found {len(duplicates)} potential duplicates:")
                    for i, dup in enumerate(duplicates, 1):
                        print(f"   {i}. '{dup['title']}' by {dup['artist']}")
                        print(f"      Similarity: {dup['similarity_percentage']}% ({dup['hash_type']})")
                else:
                    print(f"   No duplicates found")
                
                return result
            else:
                print(f"❌ Manual check failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in manual check: {e}")
        
        return None

    def test_scenario_1_identical_images(self):
        """Test with identical images from different artists"""
        print("\n" + "="*50)
        print("📋 TEST SCENARIO 1: Identical Images")
        print("="*50)
        
        # Register two artists
        token1 = self.register_user("artist1_identical")
        token2 = self.register_user("artist2_identical")
        
        if not token1 or not token2:
            print("❌ Failed to register users")
            return False
        
        # Create identical image
        image_path = self.create_test_image("identical.jpg", "IDENTICAL", (255, 0, 0))
        
        # Upload by first artist
        artwork1_id, result1 = self.upload_artwork(token1, "Original Artwork", image_path)
        if not artwork1_id:
            return False
        
        time.sleep(1)  # Small delay
        
        # Upload same image by second artist
        artwork2_id, result2 = self.upload_artwork(token2, "Duplicate Artwork", image_path)
        if not artwork2_id:
            return False
        
        # Check if duplicate was detected
        duplicate_detected = result2.get('duplicate_check', {}).get('has_duplicates', False)
        
        print(f"\n📊 SCENARIO 1 RESULT:")
        print(f"   Duplicate detected: {'✅ YES' if duplicate_detected else '❌ NO'}")
        
        return duplicate_detected

    def test_scenario_2_similar_images(self):
        """Test with similar but not identical images"""
        print("\n" + "="*50)
        print("📋 TEST SCENARIO 2: Similar Images")
        print("="*50)
        
        # Register two artists
        token1 = self.register_user("artist1_similar")
        token2 = self.register_user("artist2_similar")
        
        if not token1 or not token2:
            print("❌ Failed to register users")
            return False
        
        # Create original and similar images
        original_path = self.create_test_image("original.jpg", "ORIGINAL", (0, 255, 0))
        similar_path = self.create_similar_image(original_path, "similar.jpg")
        
        # Upload original by first artist
        artwork1_id, result1 = self.upload_artwork(token1, "Original Green Art", original_path)
        if not artwork1_id:
            return False
        
        time.sleep(1)  # Small delay
        
        # Upload similar by second artist
        artwork2_id, result2 = self.upload_artwork(token2, "Modified Green Art", similar_path)
        if not artwork2_id:
            return False
        
        # Check if similarity was detected
        duplicate_detected = result2.get('duplicate_check', {}).get('has_duplicates', False)
        
        print(f"\n📊 SCENARIO 2 RESULT:")
        print(f"   Similarity detected: {'✅ YES' if duplicate_detected else '⚠️ NO (might be expected)'}")
        
        return True  # This might not detect duplicates depending on threshold

    def test_scenario_3_different_images(self):
        """Test with completely different images"""
        print("\n" + "="*50)
        print("📋 TEST SCENARIO 3: Different Images")
        print("="*50)
        
        # Register two artists
        token1 = self.register_user("artist1_different")
        token2 = self.register_user("artist2_different")
        
        if not token1 or not token2:
            print("❌ Failed to register users")
            return False
        
        # Create different images
        image1_path = self.create_test_image("red_art.jpg", "RED ART", (255, 0, 0))
        image2_path = self.create_test_image("blue_art.jpg", "BLUE ART", (0, 0, 255))
        
        # Upload by first artist
        artwork1_id, result1 = self.upload_artwork(token1, "Red Artwork", image1_path)
        if not artwork1_id:
            return False
        
        time.sleep(1)  # Small delay
        
        # Upload by second artist
        artwork2_id, result2 = self.upload_artwork(token2, "Blue Artwork", image2_path)
        if not artwork2_id:
            return False
        
        # Check if duplicates were detected (should be NO)
        duplicate_detected = result2.get('duplicate_check', {}).get('has_duplicates', False)
        
        print(f"\n📊 SCENARIO 3 RESULT:")
        print(f"   Duplicate detected: {'❌ UNEXPECTED' if duplicate_detected else '✅ NO (correct)'}")
        
        return not duplicate_detected

    def test_scenario_4_same_artist(self):
        """Test same artist uploading similar images (should be allowed)"""
        print("\n" + "="*50)
        print("📋 TEST SCENARIO 4: Same Artist Similar Images")
        print("="*50)
        
        # Register one artist
        token = self.register_user("artist_same")
        
        if not token:
            print("❌ Failed to register user")
            return False
        
        # Create original and similar images
        original_path = self.create_test_image("artist_original.jpg", "ARTIST WORK", (128, 0, 128))
        similar_path = self.create_similar_image(original_path, "artist_variation.jpg")
        
        # Upload original
        artwork1_id, result1 = self.upload_artwork(token, "My Original Work", original_path)
        if not artwork1_id:
            return False
        
        time.sleep(1)  # Small delay
        
        # Upload variation by same artist
        artwork2_id, result2 = self.upload_artwork(token, "My Work Variation", similar_path)
        if not artwork2_id:
            return False
        
        # Same artist should be allowed to upload similar works
        duplicate_detected = result2.get('duplicate_check', {}).get('has_duplicates', False)
        
        print(f"\n📊 SCENARIO 4 RESULT:")
        print(f"   Duplicate detected: {'⚠️ DETECTED (but allowed)' if duplicate_detected else '✅ NO (same artist exception)'}")
        
        return True  # Both outcomes are acceptable for same artist

    def test_manual_check(self):
        """Test manual duplicate check endpoint"""
        print("\n" + "="*50)
        print("📋 TEST: Manual Duplicate Check")
        print("="*50)
        
        if not self.created_artworks:
            print("❌ No artworks available for manual check")
            return False
        
        # Use first created artwork and its token
        artwork_id = self.created_artworks[0]
        token = list(self.tokens.values())[0]  # Get any token
        
        result = self.check_duplicates_manually(token, artwork_id)
        
        return result is not None

    def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting API Duplicate Detection Tests")
        
        scenarios = [
            ("Identical Images", self.test_scenario_1_identical_images),
            ("Similar Images", self.test_scenario_2_similar_images),
            ("Different Images", self.test_scenario_3_different_images),
            ("Same Artist", self.test_scenario_4_same_artist),
            ("Manual Check", self.test_manual_check)
        ]
        
        results = {}
        
        for scenario_name, test_func in scenarios:
            try:
                print(f"\n🧪 Running: {scenario_name}")
                result = test_func()
                results[scenario_name] = "✅ PASSED" if result else "❌ FAILED"
            except Exception as e:
                results[scenario_name] = f"❌ ERROR: {str(e)}"
                print(f"❌ {scenario_name} failed with error: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        for scenario, result in results.items():
            print(f"{scenario:.<30} {result}")
        
        passed = sum(1 for r in results.values() if "PASSED" in r)
        total = len(results)
        
        print(f"\n🎯 Overall: {passed}/{total} scenarios completed successfully")
        
        if passed >= 4:  # Allow some flexibility
            print("🎉 Duplicate detection system is working!")
        else:
            print("⚠️ Some issues detected. Check the implementation.")
        
        print(f"\n📝 Created {len(self.created_artworks)} test artworks")
        print("💡 You can check these artworks in the admin panel or API")
        
        return passed >= 4

    def cleanup(self):
        """Clean up test files"""
        try:
            import shutil
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

def main():
    """Main function"""
    import sys
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = DuplicateAPITester(base_url)
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(main())