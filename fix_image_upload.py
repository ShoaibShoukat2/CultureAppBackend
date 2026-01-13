#!/usr/bin/env python
"""
Fix script for image upload validation issues
This script addresses common Django ImageField validation problems
"""

import os
import sys
from PIL import Image

# Add Django project to path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django
django.setup()

def fix_media_directories():
    """Create necessary media directories with proper permissions"""
    from django.conf import settings
    
    print("🔧 Creating media directories...")
    
    media_root = settings.MEDIA_ROOT
    directories = [
        media_root,
        os.path.join(media_root, 'artworks'),
        os.path.join(media_root, 'watermarked_artworks'),
        os.path.join(media_root, 'profile_images'),
        os.path.join(media_root, 'equipment'),
        os.path.join(media_root, 'message_attachments')
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created/verified: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")

def create_test_image(filename="test_valid_image.jpg", size=(800, 600)):
    """Create a valid test image for testing uploads"""
    print(f"🖼️ Creating test image: {filename}")
    
    try:
        # Create a simple test image
        img = Image.new('RGB', size, color='red')
        
        # Add some content to make it more realistic
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, size[0]-50, size[1]-50], outline='blue', width=5)
        draw.ellipse([100, 100, size[0]-100, size[1]-100], fill='green')
        
        # Try to add text (fallback if font not available)
        try:
            font = ImageFont.load_default()
            draw.text((size[0]//2-50, size[1]//2), "TEST IMAGE", fill='white', font=font)
        except:
            draw.text((size[0]//2-50, size[1]//2), "TEST IMAGE", fill='white')
        
        # Save the image
        img.save(filename, 'JPEG', quality=95)
        print(f"✅ Created test image: {filename} ({size[0]}x{size[1]})")
        
        return filename
        
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return None

def validate_image_file(image_path):
    """Validate an image file thoroughly"""
    print(f"\n🔍 Validating image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return False
    
    try:
        # Check file size
        file_size = os.path.getsize(image_path)
        print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Check if file is too large (Django default is 2.5MB)
        max_size = 2.5 * 1024 * 1024  # 2.5MB
        if file_size > max_size:
            print(f"⚠️ Warning: File size exceeds recommended limit of 2.5MB")
        
        # Try to open with PIL
        with Image.open(image_path) as img:
            print(f"🖼️ Image info: {img.format} {img.size} {img.mode}")
            
            # Check if image is corrupted by trying to load it
            img.load()
            print("✅ Image loads successfully")
            
            # Verify image
            img.verify()
            print("✅ Image verification passed")
            
        # Re-open for further checks (verify() closes the image)
        with Image.open(image_path) as img:
            # Check for common issues
            if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                print(f"⚠️ Unusual color mode: {img.mode}")
            
            if img.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'TIFF']:
                print(f"⚠️ Unusual format: {img.format}")
            
            # Check dimensions
            width, height = img.size
            if width < 1 or height < 1:
                print(f"❌ Invalid dimensions: {width}x{height}")
                return False
            
            if width > 10000 or height > 10000:
                print(f"⚠️ Very large dimensions: {width}x{height}")
        
        print("✅ Image validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Image validation failed: {type(e).__name__}: {e}")
        return False

def fix_common_image_issues(input_path, output_path=None):
    """Fix common image issues that cause Django validation to fail"""
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_fixed{ext}"
    
    print(f"🔧 Fixing image issues: {input_path} -> {output_path}")
    
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if needed (fixes CMYK, P mode issues)
            if img.mode not in ['RGB', 'RGBA']:
                print(f"🔄 Converting from {img.mode} to RGB")
                if img.mode == 'RGBA':
                    # Create white background for RGBA images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Resize if too large
            max_dimension = 2048
            if img.width > max_dimension or img.height > max_dimension:
                print(f"📏 Resizing from {img.size}")
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                print(f"📏 Resized to {img.size}")
            
            # Save with optimized settings
            save_kwargs = {
                'format': 'JPEG',
                'quality': 90,
                'optimize': True
            }
            
            if output_path.lower().endswith('.png'):
                save_kwargs = {
                    'format': 'PNG',
                    'optimize': True
                }
            
            img.save(output_path, **save_kwargs)
            print(f"✅ Fixed image saved: {output_path}")
            
            return output_path
            
    except Exception as e:
        print(f"❌ Failed to fix image: {e}")
        return None

def test_django_upload(image_path):
    """Test Django ImageField validation with the image"""
    print(f"\n🧪 Testing Django upload with: {image_path}")
    
    try:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from api.models import Artwork
        
        with open(image_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name=os.path.basename(image_path),
                content=f.read(),
                content_type='image/jpeg'
            )
        
        # Test model validation
        artwork = Artwork(
            title="Test Upload",
            description="Testing image upload validation",
            price=100.00,
            image=uploaded_file
        )
        
        # This triggers Django's validation
        artwork.full_clean()
        print("✅ Django model validation passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Django validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Django Image Upload Fix Tool")
    print("=" * 50)
    
    # Step 1: Fix media directories
    fix_media_directories()
    
    # Step 2: Create a test image
    test_image = create_test_image()
    
    if test_image:
        # Step 3: Validate the test image
        if validate_image_file(test_image):
            # Step 4: Test Django upload
            test_django_upload(test_image)
    
    # Step 5: If user provided an image file, test it
    if len(sys.argv) > 1:
        user_image = sys.argv[1]
        print(f"\n🔍 Testing user provided image: {user_image}")
        
        if validate_image_file(user_image):
            if not test_django_upload(user_image):
                # Try to fix the image
                fixed_image = fix_common_image_issues(user_image)
                if fixed_image:
                    print(f"\n🧪 Testing fixed image...")
                    test_django_upload(fixed_image)
    
    print(f"\n📋 Troubleshooting Tips:")
    print("1. Ensure your image is a valid JPEG, PNG, or GIF")
    print("2. Check file size (should be under 2.5MB)")
    print("3. Try converting CMYK images to RGB")
    print("4. Ensure proper file permissions on media directories")
    print("5. Check if Pillow is properly installed: pip install Pillow")