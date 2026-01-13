#!/usr/bin/env python
"""
Debug script to test image upload validation
Run this to check if your images are valid and identify the issue
"""

import os
import sys
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

# Add Django project to path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django
django.setup()

from api.models import Artwork
from api.serializers import ArtworkSerializer

def test_image_validation(image_path):
    """Test if an image file passes Django's ImageField validation"""
    print(f"\n=== Testing Image: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return False
    
    try:
        # Test 1: PIL can open the image
        print("1. Testing PIL image opening...")
        with Image.open(image_path) as img:
            print(f"   ✅ PIL Success: {img.format} {img.size} {img.mode}")
            
        # Test 2: File size check
        file_size = os.path.getsize(image_path)
        print(f"2. File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Test 3: Django ImageField validation
        print("3. Testing Django ImageField validation...")
        with open(image_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name=os.path.basename(image_path),
                content=f.read(),
                content_type='image/jpeg'  # You can adjust this
            )
            
            # Create a test artwork instance (don't save)
            artwork = Artwork(
                title="Test Image",
                description="Test description",
                price=100.00,
                image=uploaded_file
            )
            
            # This will trigger Django's image validation
            artwork.full_clean()
            print("   ✅ Django validation passed!")
            
        return True
        
    except ValidationError as e:
        print(f"   ❌ Django Validation Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        return False

def check_media_directory():
    """Check if media directory is properly configured"""
    print("\n=== Checking Media Directory Configuration ===")
    
    from django.conf import settings
    
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    media_url = getattr(settings, 'MEDIA_URL', None)
    
    print(f"MEDIA_ROOT: {media_root}")
    print(f"MEDIA_URL: {media_url}")
    
    if media_root:
        artworks_dir = os.path.join(media_root, 'artworks')
        print(f"Artworks directory: {artworks_dir}")
        
        if not os.path.exists(media_root):
            print(f"❌ MEDIA_ROOT directory doesn't exist: {media_root}")
            try:
                os.makedirs(media_root, exist_ok=True)
                print(f"✅ Created MEDIA_ROOT directory")
            except Exception as e:
                print(f"❌ Failed to create MEDIA_ROOT: {e}")
        else:
            print(f"✅ MEDIA_ROOT exists")
            
        if not os.path.exists(artworks_dir):
            try:
                os.makedirs(artworks_dir, exist_ok=True)
                print(f"✅ Created artworks directory")
            except Exception as e:
                print(f"❌ Failed to create artworks directory: {e}")
        else:
            print(f"✅ Artworks directory exists")

def check_django_settings():
    """Check Django settings that might affect file uploads"""
    print("\n=== Checking Django Settings ===")
    
    from django.conf import settings
    
    # File upload settings
    settings_to_check = [
        'FILE_UPLOAD_MAX_MEMORY_SIZE',
        'DATA_UPLOAD_MAX_MEMORY_SIZE', 
        'DATA_UPLOAD_MAX_NUMBER_FIELDS',
        'FILE_UPLOAD_PERMISSIONS',
        'FILE_UPLOAD_DIRECTORY_PERMISSIONS'
    ]
    
    for setting_name in settings_to_check:
        value = getattr(settings, setting_name, 'Not set')
        print(f"{setting_name}: {value}")

if __name__ == "__main__":
    print("🔍 Django Image Upload Debug Tool")
    print("=" * 50)
    
    # Check Django configuration
    check_django_settings()
    check_media_directory()
    
    # Test with sample images if they exist
    test_images = [
        'test_image.jpg',
        'test_image.png',
        'sample.jpg',
        'sample.png'
    ]
    
    print(f"\n=== Testing Sample Images ===")
    print("Place test images in the project root and run this script")
    
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image_validation(img_path)
    
    print(f"\n=== Manual Testing Instructions ===")
    print("1. Place a test image file in the project root")
    print("2. Run: python debug_image_upload.py <image_filename>")
    print("3. Check the output for specific validation errors")
    
    # If command line argument provided, test that image
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_image_validation(image_path)