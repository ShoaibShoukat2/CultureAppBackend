#!/usr/bin/env python
"""
Test script to verify image upload fixes are working
"""

import os
import sys
from PIL import Image

# Add Django project to path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from api.serializers import ArtworkSerializer
from api.models import CustomUser, Category

def create_test_image(filename="test_upload.jpg", size=(800, 600)):
    """Create a valid test image"""
    print(f"Creating test image: {filename}")
    
    img = Image.new('RGB', size, color='lightblue')
    
    # Add some content
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, size[0]-50, size[1]-50], outline='darkblue', width=3)
    draw.ellipse([100, 100, size[0]-100, size[1]-100], fill='yellow')
    
    img.save(filename, 'JPEG', quality=95)
    print(f"✅ Created: {filename}")
    return filename

def test_serializer_validation():
    """Test the updated serializer validation"""
    print("\n🧪 Testing ArtworkSerializer validation...")
    
    # Create test image
    test_image = create_test_image()
    
    try:
        # Create uploaded file
        with open(test_image, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name=test_image,
                content=f.read(),
                content_type='image/jpeg'
            )
        
        # Test serializer validation
        data = {
            'title': 'Test Artwork',
            'description': 'Testing image upload validation',
            'price': 100.00,
            'artwork_type': 'digital',
            'image': uploaded_file
        }
        
        # Create a mock request context
        class MockRequest:
            def __init__(self):
                self.user = None
        
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = 'testartist'
                self.user_type = 'artist'
        
        mock_request = MockRequest()
        mock_request.user = MockUser()
        
        serializer = ArtworkSerializer(data=data, context={'request': mock_request})
        
        if serializer.is_valid():
            print("✅ Serializer validation passed!")
            print(f"   Validated data keys: {list(serializer.validated_data.keys())}")
            return True
        else:
            print("❌ Serializer validation failed:")
            for field, errors in serializer.errors.items():
                print(f"   {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    finally:
        # Clean up test file
        if os.path.exists(test_image):
            os.remove(test_image)

def test_invalid_images():
    """Test validation with invalid images"""
    print("\n🧪 Testing invalid image validation...")
    
    # Test 1: Create a text file with image extension
    fake_image = "fake_image.jpg"
    with open(fake_image, 'w') as f:
        f.write("This is not an image file")
    
    try:
        with open(fake_image, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name=fake_image,
                content=f.read(),
                content_type='image/jpeg'
            )
        
        data = {
            'title': 'Test Invalid',
            'description': 'Testing invalid image',
            'price': 100.00,
            'image': uploaded_file
        }
        
        class MockRequest:
            def __init__(self):
                self.user = None
        
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = 'testartist'
                self.user_type = 'artist'
        
        mock_request = MockRequest()
        mock_request.user = MockUser()
        
        serializer = ArtworkSerializer(data=data, context={'request': mock_request})
        
        if serializer.is_valid():
            print("❌ Validation should have failed for fake image!")
            return False
        else:
            print("✅ Correctly rejected invalid image:")
            for field, errors in serializer.errors.items():
                print(f"   {field}: {errors}")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    finally:
        # Clean up
        if os.path.exists(fake_image):
            os.remove(fake_image)

def check_settings():
    """Check if settings are properly configured"""
    print("\n⚙️ Checking Django settings...")
    
    from django.conf import settings
    
    settings_to_check = [
        ('FILE_UPLOAD_MAX_MEMORY_SIZE', '10MB'),
        ('DATA_UPLOAD_MAX_MEMORY_SIZE', '10MB'),
        ('MAX_IMAGE_SIZE', '5MB'),
        ('ALLOWED_IMAGE_EXTENSIONS', 'Image formats'),
    ]
    
    for setting_name, description in settings_to_check:
        value = getattr(settings, setting_name, 'Not set')
        if isinstance(value, int) and 'SIZE' in setting_name:
            value_mb = value / 1024 / 1024
            print(f"✅ {setting_name}: {value:,} bytes ({value_mb:.1f}MB)")
        else:
            print(f"✅ {setting_name}: {value}")

if __name__ == "__main__":
    print("🔧 Testing Image Upload Fixes")
    print("=" * 50)
    
    # Check settings
    check_settings()
    
    # Test valid image
    valid_test = test_serializer_validation()
    
    # Test invalid image
    invalid_test = test_invalid_images()
    
    print(f"\n📊 Test Results:")
    print(f"Valid image test: {'✅ PASS' if valid_test else '❌ FAIL'}")
    print(f"Invalid image test: {'✅ PASS' if invalid_test else '❌ FAIL'}")
    
    if valid_test and invalid_test:
        print(f"\n🎉 All tests passed! Image upload validation is working correctly.")
        print(f"\n📋 Next steps:")
        print(f"1. Test with your frontend application")
        print(f"2. Try uploading different image formats (JPEG, PNG, GIF)")
        print(f"3. Test with various file sizes")
        print(f"4. Check error messages are user-friendly")
    else:
        print(f"\n⚠️ Some tests failed. Check the error messages above.")
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Ensure Pillow is installed: pip install Pillow")
        print(f"2. Check media directory permissions")
        print(f"3. Verify Django settings are correct")
        print(f"4. Test with a simple, small JPEG image first")