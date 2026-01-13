"""
Custom image validators for Django ImageField
Add better error messages and validation for image uploads
"""

from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import os


def validate_image_file(image_field):
    """
    Comprehensive image validation function
    
    Args:
        image_field: Django ImageField or uploaded file
        
    Raises:
        ValidationError: If image validation fails
    """
    if not image_field:
        raise ValidationError("Image file is required.")
    
    # Check file size
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)  # Default 5MB
    if hasattr(image_field, 'size') and image_field.size > max_size:
        raise ValidationError(
            f"Image file too large. Maximum size allowed is {max_size/1024/1024:.1f}MB. "
            f"Your file is {image_field.size/1024/1024:.1f}MB."
        )
    
    # Check file extension
    allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', 
                                ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
    
    if hasattr(image_field, 'name'):
        file_extension = os.path.splitext(image_field.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"Unsupported file format '{file_extension}'. "
                f"Allowed formats: {', '.join(allowed_extensions)}"
            )
    
    # Validate image content using PIL
    try:
        # Reset file pointer to beginning if possible
        if hasattr(image_field, 'seek'):
            image_field.seek(0)
        
        # Open and validate the image
        with Image.open(image_field) as img:
            # Get image info before verification
            width, height = img.size
            format_name = img.format
            mode = img.mode
            
            # Check image dimensions
            min_dimension = getattr(settings, 'MIN_IMAGE_DIMENSION', 100)
            max_dimension = getattr(settings, 'MAX_IMAGE_DIMENSION', 10000)
            
            if width < min_dimension or height < min_dimension:
                raise ValidationError(
                    f"Image too small. Minimum size is {min_dimension}x{min_dimension} pixels. "
                    f"Your image is {width}x{height} pixels."
                )
            
            if width > max_dimension or height > max_dimension:
                raise ValidationError(
                    f"Image too large. Maximum size is {max_dimension}x{max_dimension} pixels. "
                    f"Your image is {width}x{height} pixels."
                )
            
            # Check color mode
            if mode not in ['RGB', 'RGBA', 'L', 'P']:
                raise ValidationError(
                    f"Unsupported color mode '{mode}'. "
                    f"Please convert your image to RGB format."
                )
            
            # Check format
            if format_name not in ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']:
                raise ValidationError(
                    f"Unsupported image format '{format_name}'. "
                    f"Please use JPEG, PNG, GIF, BMP, or WebP format."
                )
            
            # Try to load the image data to check for corruption
            try:
                img.load()
            except Exception as load_error:
                raise ValidationError(
                    f"Image appears to be corrupted: {str(load_error)}"
                )
    
    except ValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        # Handle PIL errors and other exceptions
        error_msg = str(e).lower()
        
        if 'cannot identify image file' in error_msg:
            raise ValidationError(
                "Invalid image file. The file you uploaded was either not an image or a corrupted image. "
                "Please ensure you're uploading a valid JPEG, PNG, GIF, BMP, or WebP file."
            )
        elif 'truncated' in error_msg or 'incomplete' in error_msg:
            raise ValidationError(
                "Incomplete image file. The image appears to be corrupted or was not fully uploaded. "
                "Please try uploading the image again."
            )
        elif 'decoder' in error_msg:
            raise ValidationError(
                "Image decoding error. The image format may be corrupted or unsupported. "
                "Please try converting your image to JPEG or PNG format."
            )
        elif 'permission' in error_msg or 'access' in error_msg:
            raise ValidationError(
                "File access error. Please try uploading the image again."
            )
        else:
            raise ValidationError(
                f"Upload a valid image. The file you uploaded was either not an image or a corrupted image. "
                f"Error details: {str(e)}"
            )
    
    finally:
        # Reset file pointer if possible
        if hasattr(image_field, 'seek'):
            try:
                image_field.seek(0)
            except:
                pass


def validate_artwork_image(image_field):
    """
    Specific validator for artwork images
    """
    validate_image_file(image_field)
    
    # Additional artwork-specific validations can go here
    # For example, checking aspect ratio, minimum quality, etc.
    
    return image_field


def validate_profile_image(image_field):
    """
    Specific validator for profile images
    """
    validate_image_file(image_field)
    
    # Additional profile image validations
    try:
        if hasattr(image_field, 'seek'):
            image_field.seek(0)
        
        with Image.open(image_field) as img:
            width, height = img.size
            
            # Profile images should be somewhat square
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 3:  # Allow up to 3:1 aspect ratio
                raise ValidationError(
                    f"Profile image aspect ratio too extreme. "
                    f"Please use an image with a more square aspect ratio. "
                    f"Current ratio: {aspect_ratio:.1f}:1"
                )
    
    except ValidationError:
        raise
    except Exception:
        # If we can't check aspect ratio, that's okay
        pass
    
    finally:
        if hasattr(image_field, 'seek'):
            try:
                image_field.seek(0)
            except:
                pass
    
    return image_field