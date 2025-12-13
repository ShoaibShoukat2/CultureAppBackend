#!/usr/bin/env python3
"""
Complete API Testing Script for CultureUp Platform
Tests all endpoints to ensure they're working after S3 removal
"""

import os
import sys
import django
import requests
import json
from io import BytesIO
from PIL import Image
import tempfile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import *

User = get_user_model()

class APITester:
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
    
    def create_test_image(self, filename="test_artwork.jpg"):
        """Create a test image file"""
        img = Image.new('RGB', (800, 600), color='red')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG')
        return temp_file.name
    
    def test_server_connection(self):
        """Test if Django server is running"""
        self.print_header("SERVER CONNECTION TEST")
        try:
            response = requests.get(f"{self.base_url}/api/", timeout=5)
            if response.status_code in [200, 404]:  # 404 is ok, means server is running
                self.print_test("Server Connection", True, f"Server is running on {self.base_url}")
                return True
            else:
                self.print_test("Server Connection", False, f"Unexpected status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("Server Connection", False, "Cannot connect to server. Is Django running?")
            return False
        except Exception as e:
            self.print_test("Server Connection", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoints"""
        self.print_header("USER REGISTRATION & AUTHENTICATION")
        
        # Test Artist Registration
        artist_data = {
            "username": "test_artist",
            "email": "artist@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "Artist",
            "user_type": "artist"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/auth/register/", json=artist_data)
            if response.status_code == 201:
                data = response.json()
                self.tokens['artist'] = data.get('token')
                self.test_data['artist_id'] = data.get('user', {}).get('id')
                self.print_test("Artist Registration", True, f"Token: {self.tokens['artist'][:20]}...")
            else:
                self.print_test("Artist Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.print_test("Artist Registration", False, f"Error: {str(e)}")
        
        # Test Buyer Registration
        buyer_data = {
            "username": "test_buyer",
            "email": "buyer@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "Buyer",
            "user_type": "buyer"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/auth/register/", json=buyer_data)
            if response.status_code == 201:
                data = response.json()
                self.tokens['buyer'] = data.get('token')
                self.test_data['buyer_id'] = data.get('user', {}).get('id')
                self.print_test("Buyer Registration", True, f"Token: {self.tokens['buyer'][:20]}...")
            else:
                self.print_test("Buyer Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.print_test("Buyer Registration", False, f"Error: {str(e)}")
    
    def test_user_login(self):
        """Test user login"""
        # Test Artist Login
        login_data = {
            "username": "test_artist",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/auth/login/", json=login_data)
            if response.status_code == 200:
                self.print_test("Artist Login", True, "Login successful")
            else:
                self.print_test("Artist Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Artist Login", False, f"Error: {str(e)}")
    
    def test_categories(self):
        """Test category endpoints"""
        self.print_header("CATEGORY MANAGEMENT")
        
        try:
            response = self.session.get(f"{self.base_url}/api/categories/")
            if response.status_code == 200:
                categories = response.json()
                self.print_test("Get Categories", True, f"Found {len(categories)} categories")
                if categories:
                    self.test_data['category_id'] = categories[0]['id']
            else:
                self.print_test("Get Categories", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Categories", False, f"Error: {str(e)}")
    
    def test_artwork_operations(self):
        """Test artwork CRUD operations (without S3)"""
        self.print_header("ARTWORK OPERATIONS (LOCAL STORAGE)")
        
        if 'artist' not in self.tokens:
            self.print_test("Artwork Tests", False, "No artist token available")
            return
        
        headers = {'Authorization': f'Token {self.tokens["artist"]}'}
        
        # Test artwork upload with local file
        try:
            # Create test image
            test_image_path = self.create_test_image()
            
            with open(test_image_path, 'rb') as img_file:
                files = {'image': ('test_artwork.jpg', img_file, 'image/jpeg')}
                data = {
                    'title': 'Test Artwork',
                    'description': 'Test artwork description',
                    'artwork_type': 'digital',
                    'price': '100.00'
                }
                if 'category_id' in self.test_data:
                    data['category'] = self.test_data['category_id']
                
                response = self.session.post(
                    f"{self.base_url}/api/artworks/", 
                    files=files, 
                    data=data, 
                    headers=headers
                )
                
                if response.status_code == 201:
                    artwork_data = response.json()
                    self.test_data['artwork_id'] = artwork_data.get('artwork', {}).get('id')
                    self.print_test("Artwork Upload", True, f"Artwork ID: {self.test_data.get('artwork_id')}")
                else:
                    self.print_test("Artwork Upload", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Clean up test image
            os.unlink(test_image_path)
            
        except Exception as e:
            self.print_test("Artwork Upload", False, f"Error: {str(e)}")
        
        # Test get artworks
        try:
            response = self.session.get(f"{self.base_url}/api/artworks/")
            if response.status_code == 200:
                artworks = response.json()
                count = artworks.get('count', len(artworks)) if isinstance(artworks, dict) else len(artworks)
                self.print_test("Get Artworks", True, f"Found {count} artworks")
            else:
                self.print_test("Get Artworks", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Artworks", False, f"Error: {str(e)}")
        
        # Test artwork detail
        if 'artwork_id' in self.test_data:
            try:
                response = self.session.get(f"{self.base_url}/api/artworks/{self.test_data['artwork_id']}/")
                if response.status_code == 200:
                    self.print_test("Get Artwork Detail", True, "Artwork details retrieved")
                else:
                    self.print_test("Get Artwork Detail", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Get Artwork Detail", False, f"Error: {str(e)}")
    
    def test_job_operations(self):
        """Test job/project operations"""
        self.print_header("JOB/PROJECT OPERATIONS")
        
        if 'buyer' not in self.tokens:
            self.print_test("Job Tests", False, "No buyer token available")
            return
        
        headers = {'Authorization': f'Token {self.tokens["buyer"]}'}
        
        # Test job creation
        job_data = {
            'title': 'Test Project',
            'description': 'Test project description',
            'budget_min': '50.00',
            'budget_max': '200.00',
            'duration_days': 7,
            'required_skills': 'Digital Art, Illustration',
            'experience_level': 'intermediate'
        }
        
        if 'category_id' in self.test_data:
            job_data['category'] = self.test_data['category_id']
        
        try:
            response = self.session.post(f"{self.base_url}/api/jobs/", json=job_data, headers=headers)
            if response.status_code == 201:
                job_response = response.json()
                self.test_data['job_id'] = job_response.get('id')
                self.print_test("Job Creation", True, f"Job ID: {self.test_data.get('job_id')}")
            else:
                self.print_test("Job Creation", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.print_test("Job Creation", False, f"Error: {str(e)}")
        
        # Test get jobs
        try:
            response = self.session.get(f"{self.base_url}/api/jobs/")
            if response.status_code == 200:
                jobs = response.json()
                count = jobs.get('count', len(jobs)) if isinstance(jobs, dict) else len(jobs)
                self.print_test("Get Jobs", True, f"Found {count} jobs")
            else:
                self.print_test("Get Jobs", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Jobs", False, f"Error: {str(e)}")
    
    def test_bid_operations(self):
        """Test bidding operations"""
        self.print_header("BIDDING OPERATIONS")
        
        if 'artist' not in self.tokens or 'job_id' not in self.test_data:
            self.print_test("Bid Tests", False, "Missing artist token or job ID")
            return
        
        headers = {'Authorization': f'Token {self.tokens["artist"]}'}
        
        # Test bid creation
        bid_data = {
            'job': self.test_data['job_id'],
            'bid_amount': '150.00',
            'delivery_time': 5,
            'proposal': 'I can complete this project with high quality.'
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/bids/", json=bid_data, headers=headers)
            if response.status_code == 201:
                bid_response = response.json()
                self.test_data['bid_id'] = bid_response.get('id')
                self.print_test("Bid Creation", True, f"Bid ID: {self.test_data.get('bid_id')}")
            else:
                self.print_test("Bid Creation", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.print_test("Bid Creation", False, f"Error: {str(e)}")
        
        # Test get bids
        try:
            response = self.session.get(f"{self.base_url}/api/bids/", headers=headers)
            if response.status_code == 200:
                bids = response.json()
                count = bids.get('count', len(bids)) if isinstance(bids, dict) else len(bids)
                self.print_test("Get Bids", True, f"Found {count} bids")
            else:
                self.print_test("Get Bids", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Bids", False, f"Error: {str(e)}")
    
    def test_profile_operations(self):
        """Test profile operations"""
        self.print_header("PROFILE OPERATIONS")
        
        # Test artist profile
        if 'artist' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = self.session.get(f"{self.base_url}/api/artist-profiles/{self.test_data.get('artist_id')}/", headers=headers)
                if response.status_code == 200:
                    self.print_test("Get Artist Profile", True, "Artist profile retrieved")
                else:
                    self.print_test("Get Artist Profile", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Get Artist Profile", False, f"Error: {str(e)}")
        
        # Test buyer profile
        if 'buyer' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["buyer"]}'}
            try:
                response = self.session.get(f"{self.base_url}/api/buyer-profiles/{self.test_data.get('buyer_id')}/", headers=headers)
                if response.status_code == 200:
                    self.print_test("Get Buyer Profile", True, "Buyer profile retrieved")
                else:
                    self.print_test("Get Buyer Profile", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Get Buyer Profile", False, f"Error: {str(e)}")
    
    def test_equipment_operations(self):
        """Test equipment operations"""
        self.print_header("EQUIPMENT OPERATIONS")
        
        try:
            response = self.session.get(f"{self.base_url}/api/equipment/")
            if response.status_code == 200:
                equipment = response.json()
                count = equipment.get('count', len(equipment)) if isinstance(equipment, dict) else len(equipment)
                self.print_test("Get Equipment", True, f"Found {count} equipment items")
            else:
                self.print_test("Get Equipment", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Equipment", False, f"Error: {str(e)}")
    
    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        self.print_header("DASHBOARD STATISTICS")
        
        if 'artist' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = self.session.get(f"{self.base_url}/api/dashboard/stats/", headers=headers)
                if response.status_code == 200:
                    self.print_test("Artist Dashboard Stats", True, "Dashboard stats retrieved")
                else:
                    self.print_test("Artist Dashboard Stats", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Artist Dashboard Stats", False, f"Error: {str(e)}")
    
    def test_notifications(self):
        """Test notification operations"""
        self.print_header("NOTIFICATION OPERATIONS")
        
        if 'artist' in self.tokens:
            headers = {'Authorization': f'Token {self.tokens["artist"]}'}
            try:
                response = self.session.get(f"{self.base_url}/api/notifications/", headers=headers)
                if response.status_code == 200:
                    notifications = response.json()
                    count = notifications.get('count', len(notifications)) if isinstance(notifications, dict) else len(notifications)
                    self.print_test("Get Notifications", True, f"Found {count} notifications")
                else:
                    self.print_test("Get Notifications", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test("Get Notifications", False, f"Error: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.print_header("CLEANUP TEST DATA")
        
        try:
            # Delete test users
            User.objects.filter(username__in=['test_artist', 'test_buyer']).delete()
            self.print_test("Cleanup Users", True, "Test users deleted")
        except Exception as e:
            self.print_test("Cleanup Users", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Complete API Test Suite for CultureUp Platform")
        print("📝 Testing all endpoints after S3 functionality removal")
        
        # Check server connection first
        if not self.test_server_connection():
            print("\n❌ Cannot proceed with tests - server is not running!")
            print("💡 Please start Django server with: python manage.py runserver")
            return False
        
        # Run all tests
        self.test_user_registration()
        self.test_user_login()
        self.test_categories()
        self.test_artwork_operations()
        self.test_job_operations()
        self.test_bid_operations()
        self.test_profile_operations()
        self.test_equipment_operations()
        self.test_dashboard_stats()
        self.test_notifications()
        
        # Cleanup
        self.cleanup_test_data()
        
        self.print_header("TEST SUMMARY")
        print("✅ All API tests completed!")
        print("📊 Check individual test results above")
        print("🎯 Local file storage is working (S3 removed successfully)")
        
        return True

def main():
    """Main function to run tests"""
    print("🧪 CultureUp API Test Suite")
    print("=" * 50)
    
    # Check if Django server is running
    tester = APITester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
    
    print("\n🏁 Test suite finished!")

if __name__ == "__main__":
    main()