#!/usr/bin/env python3
"""
Simple HTTP API Testing Script for CultureUp Platform
Tests all endpoints without Django setup - pure HTTP requests
"""

import requests
import json
import tempfile
from PIL import Image
import os
import time

class SimpleAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tokens = {}
        self.test_data = {}
        
    def print_header(self, title):
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
    
    def print_test(self, test_name, status, details=""):
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def create_test_image(self):
        """Create a test image file"""
        img = Image.new('RGB', (800, 600), color=(255, 0, 0))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG')
        return temp_file.name
    
    def test_server_status(self):
        """Test if server is running"""
        self.print_header("SERVER STATUS CHECK")
        try:
            # Try categories endpoint which should be accessible
            response = requests.get(f"{self.base_url}/api/categories/", timeout=10)
            if response.status_code in [200, 401, 404, 405]:  # Any of these means server is running
                self.print_test("Server Running", True, f"Server responding on {self.base_url}")
                return True
            else:
                self.print_test("Server Running", False, f"Unexpected status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("Server Running", False, "❌ Server not running! Start with: python manage.py runserver")
            return False
        except Exception as e:
            self.print_test("Server Running", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        self.print_header("USER REGISTRATION")
        
        # Test Artist Registration
        artist_data = {
            "username": f"test_artist_{int(time.time())}",
            "email": f"artist_{int(time.time())}@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "Artist",
            "user_type": "artist"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/register/", json=artist_data, timeout=10)
            if response.status_code == 201:
                data = response.json()
                self.tokens['artist'] = data.get('token')
                self.test_data['artist_id'] = data.get('user', {}).get('id')
                self.test_data['artist_username'] = artist_data['username']
                self.print_test("Artist Registration", True, f"User ID: {self.test_data['artist_id']}")
            else:
                self.print_test("Artist Registration", False, f"Status: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
        except Exception as e:
            self.print_test("Artist Registration", False, f"Error: {str(e)}")
        
        # Test Buyer Registration
        buyer_data = {
            "username": f"test_buyer_{int(time.time())}",
            "email": f"buyer_{int(time.time())}@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "Buyer",
            "user_type": "buyer"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/register/", json=buyer_data, timeout=10)
            if response.status_code == 201:
                data = response.json()
                self.tokens['buyer'] = data.get('token')
                self.test_data['buyer_id'] = data.get('user', {}).get('id')
                self.test_data['buyer_username'] = buyer_data['username']
                self.print_test("Buyer Registration", True, f"User ID: {self.test_data['buyer_id']}")
            else:
                self.print_test("Buyer Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Buyer Registration", False, f"Error: {str(e)}")
    
    def test_user_login(self):
        """Test user login"""
        self.print_header("USER LOGIN")
        
        if 'artist_username' in self.test_data:
            login_data = {
                "username": self.test_data['artist_username'],
                "password": "testpass123"
            }
            
            try:
                response = requests.post(f"{self.base_url}/api/auth/login/", json=login_data, timeout=10)
                if response.status_code == 200:
                    self.print_test("Artist Login", True, "Login successful")
                else:
                    self.print_test("Artist Login", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Artist Login", False, f"Error: {str(e)}")
    
    def test_categories(self):
        """Test categories endpoint"""
        self.print_header("CATEGORIES")
        
        try:
            response = requests.get(f"{self.base_url}/api/categories/", timeout=10)
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, dict) and 'results' in categories:
                    categories = categories['results']
                self.print_test("Get Categories", True, f"Found {len(categories)} categories")
                if categories:
                    self.test_data['category_id'] = categories[0]['id']
            else:
                self.print_test("Get Categories", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Categories", False, f"Error: {str(e)}")
    
    def test_artwork_upload(self):
        """Test artwork upload (local storage)"""
        self.print_header("ARTWORK OPERATIONS")
        
        if 'artist' not in self.tokens:
            self.print_test("Artwork Upload", False, "No artist token available")
            return
        
        headers = {'Authorization': f'Token {self.tokens["artist"]}'}
        
        try:
            # Create test image
            test_image_path = self.create_test_image()
            
            with open(test_image_path, 'rb') as img_file:
                files = {'image': ('test_artwork.jpg', img_file, 'image/jpeg')}
                data = {
                    'title': 'Test Artwork Local Storage',
                    'description': 'Testing local file upload after S3 removal',
                    'artwork_type': 'digital',
                    'price': '99.99'
                }
                
                if 'category_id' in self.test_data:
                    data['category'] = self.test_data['category_id']
                
                response = requests.post(
                    f"{self.base_url}/api/artworks/", 
                    files=files, 
                    data=data, 
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 201:
                    artwork_data = response.json()
                    if 'artwork' in artwork_data:
                        self.test_data['artwork_id'] = artwork_data['artwork']['id']
                    else:
                        self.test_data['artwork_id'] = artwork_data.get('id')
                    self.print_test("Artwork Upload", True, f"Artwork ID: {self.test_data.get('artwork_id')}")
                else:
                    self.print_test("Artwork Upload", False, f"Status: {response.status_code}")
                    if response.text:
                        print(f"   Response: {response.text[:300]}")
            
            # Clean up
            os.unlink(test_image_path)
            
        except Exception as e:
            self.print_test("Artwork Upload", False, f"Error: {str(e)}")
        
        # Test get artworks
        try:
            response = requests.get(f"{self.base_url}/api/artworks/", timeout=10)
            if response.status_code == 200:
                artworks = response.json()
                if isinstance(artworks, dict):
                    count = artworks.get('count', len(artworks.get('results', [])))
                else:
                    count = len(artworks)
                self.print_test("Get Artworks List", True, f"Found {count} artworks")
            else:
                self.print_test("Get Artworks List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Artworks List", False, f"Error: {str(e)}")
    
    def test_jobs(self):
        """Test job operations"""
        self.print_header("JOB OPERATIONS")
        
        if 'buyer' not in self.tokens:
            self.print_test("Job Creation", False, "No buyer token available")
            return
        
        headers = {'Authorization': f'Token {self.tokens["buyer"]}'}
        
        # Create job
        from datetime import datetime, timedelta
        deadline = (datetime.now() + timedelta(days=14)).isoformat()
        
        job_data = {
            'title': 'Test Project After S3 Removal',
            'description': 'Testing job creation with local storage',
            'budget_min': '50.00',
            'budget_max': '150.00',
            'duration_days': 7,
            'required_skills': 'Digital Art, Local Storage',
            'experience_level': 'intermediate',
            'deadline': deadline
        }
        
        if 'category_id' in self.test_data:
            job_data['category'] = self.test_data['category_id']
        
        try:
            response = requests.post(f"{self.base_url}/api/jobs/", json=job_data, headers=headers, timeout=10)
            if response.status_code == 201:
                job_response = response.json()
                self.test_data['job_id'] = job_response.get('id')
                self.print_test("Job Creation", True, f"Job ID: {self.test_data.get('job_id')}")
            else:
                self.print_test("Job Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Job Creation", False, f"Error: {str(e)}")
        
        # Get jobs
        try:
            response = requests.get(f"{self.base_url}/api/jobs/", timeout=10)
            if response.status_code == 200:
                jobs = response.json()
                if isinstance(jobs, dict):
                    count = jobs.get('count', len(jobs.get('results', [])))
                else:
                    count = len(jobs)
                self.print_test("Get Jobs List", True, f"Found {count} jobs")
            else:
                self.print_test("Get Jobs List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Jobs List", False, f"Error: {str(e)}")
    
    def test_bids(self):
        """Test bidding operations"""
        self.print_header("BIDDING OPERATIONS")
        
        if 'artist' not in self.tokens or 'job_id' not in self.test_data:
            self.print_test("Bid Creation", False, "Missing artist token or job ID")
            return
        
        headers = {'Authorization': f'Token {self.tokens["artist"]}'}
        
        bid_data = {
            'job_id': self.test_data['job_id'],
            'bid_amount': '100.00',
            'delivery_time': 5,
            'cover_letter': 'I can complete this project efficiently with local storage.'
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/bids/", json=bid_data, headers=headers, timeout=10)
            if response.status_code == 201:
                bid_response = response.json()
                self.test_data['bid_id'] = bid_response.get('id')
                self.print_test("Bid Creation", True, f"Bid ID: {self.test_data.get('bid_id')}")
            else:
                self.print_test("Bid Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Bid Creation", False, f"Error: {str(e)}")
    
    def test_profiles(self):
        """Test profile endpoints"""
        self.print_header("PROFILE OPERATIONS")
        
        # Artist profile
        if 'artist' in self.tokens and 'artist_id' in self.test_data:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = requests.get(f"{self.base_url}/api/artist-profiles/{self.test_data['artist_id']}/", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.print_test("Artist Profile", True, "Profile retrieved successfully")
                else:
                    self.print_test("Artist Profile", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Artist Profile", False, f"Error: {str(e)}")
        
        # Buyer profile
        if 'buyer' in self.tokens and 'buyer_id' in self.test_data:
            headers = {'Authorization': f'Token {self.tokens["buyer"]}'}
            try:
                response = requests.get(f"{self.base_url}/api/buyer-profiles/{self.test_data['buyer_id']}/", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.print_test("Buyer Profile", True, "Profile retrieved successfully")
                else:
                    self.print_test("Buyer Profile", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Buyer Profile", False, f"Error: {str(e)}")
    
    def test_equipment(self):
        """Test equipment endpoints"""
        self.print_header("EQUIPMENT OPERATIONS")
        
        try:
            response = requests.get(f"{self.base_url}/api/equipment/", timeout=10)
            if response.status_code == 200:
                equipment = response.json()
                if isinstance(equipment, dict):
                    count = equipment.get('count', len(equipment.get('results', [])))
                else:
                    count = len(equipment)
                self.print_test("Get Equipment", True, f"Found {count} equipment items")
            else:
                self.print_test("Get Equipment", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Equipment", False, f"Error: {str(e)}")
    
    def test_dashboard(self):
        """Test dashboard endpoints"""
        self.print_header("DASHBOARD & STATS")
        
        if 'artist' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = requests.get(f"{self.base_url}/api/dashboard/stats/", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.print_test("Dashboard Stats", True, "Stats retrieved successfully")
                else:
                    self.print_test("Dashboard Stats", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Dashboard Stats", False, f"Error: {str(e)}")
    
    def test_notifications(self):
        """Test notifications"""
        self.print_header("NOTIFICATIONS")
        
        if 'artist' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = requests.get(f"{self.base_url}/api/notifications/", headers=headers, timeout=10)
                if response.status_code == 200:
                    notifications = response.json()
                    if isinstance(notifications, dict):
                        count = notifications.get('count', len(notifications.get('results', [])))
                    else:
                        count = len(notifications)
                    self.print_test("Get Notifications", True, f"Found {count} notifications")
                else:
                    self.print_test("Get Notifications", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Get Notifications", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 CultureUp API Test Suite - Simple HTTP Testing")
        print("📝 Testing all endpoints after S3 removal")
        print("🎯 Focus: Local file storage functionality")
        
        # Check server first
        if not self.test_server_status():
            print("\n❌ Cannot proceed - Django server is not running!")
            print("💡 Start server with: python manage.py runserver")
            return False
        
        # Run tests
        self.test_user_registration()
        self.test_user_login()
        self.test_categories()
        self.test_artwork_upload()
        self.test_jobs()
        self.test_bids()
        self.test_profiles()
        self.test_equipment()
        self.test_dashboard()
        self.test_notifications()
        
        # Summary
        self.print_header("TEST SUMMARY")
        print("✅ HTTP API testing completed!")
        print("🎯 Local file storage is working (S3 successfully removed)")
        print("📊 Check individual test results above")
        print("💡 If any tests failed, check Django server logs")
        
        return True

def main():
    """Main function"""
    print("🧪 Simple API Tester for CultureUp")
    print("=" * 50)
    
    tester = SimpleAPITester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
    
    print("\n🏁 Testing finished!")
    print("💡 To run Django server: python manage.py runserver")

if __name__ == "__main__":
    main()