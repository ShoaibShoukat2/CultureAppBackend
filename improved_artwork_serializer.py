# Improved ArtworkSerializer with better image validation
# Add this to your api/serializers.py or replace the existing ArtworkSerializer

from rest_framework import serializers
from django.core.exceptions import ValidationError
from PIL import Image
import os

class ImprovedArtworkSerializer(serializers.ModelSerializer):
    artist = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    is_liked = serializers.SerializerMethodField()
    has_duplicates = serializers.SerializerMethodField()
    
    class Meta:
        model = Artwork
        fields = ['id', 'artist', 'title', 'description', 'category', 'category_id',
                 'artwork_type', 'price', 'image', 'watermarked_image', 'is_available',
                 'is_featured', 'views_count', 'likes_count', 'is_liked', 'has_duplicates',
                 'created_at', 'updated_at']
        read_only_fields = ['artist', 'views_count', 'likes_count', 'watermarked_image', 
                           'is_liked', 'has_duplicates']
    
    def validate_image(self, value):
        """
        Custom image validation with detailed error messages
        """
        if not value:
            raise serializers.ValidationError("Image file is required.")
        
        # Check file size (limit to 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Image file too large. Maximum size is {max_size/1024/1024:.1f}MB. "
                f"Your file is {value.size/1024/1024:.1f}MB."
            )
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_extension = os.path.splitext(value.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format '{file_extension}'. "
                f"Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Validate image content using PIL
        try:
            # Reset file pointer to beginning
            value.seek(0)
            
            # Try to open and verify the image
            with Image.open(value) as img:
                # Verify the image is not corrupted
                img.verify()
                
                # Reset file pointer again after verify()
                value.seek(0)
                
                # Re-open to get image info (verify() closes the image)
                with Image.open(value) as img:
                    # Check image dimensions
                    width, height = img.size
                    
                    if width < 100 or height < 100:
                        raise serializers.ValidationError(
                            f"Image too small. Minimum size is 100x100 pixels. "
                            f"Your image is {width}x{height} pixels."
                        )
                    
                    if width > 10000 or height > 10000:
                        raise serializers.ValidationError(
                            f"Image too large. Maximum size is 10000x10000 pixels. "
                            f"Your image is {width}x{height} pixels."
                        )
                    
                    # Check color mode
                    if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                        raise serializers.ValidationError(
                            f"Unsupported color mode '{img.mode}'. "
                            f"Please convert your image to RGB format."
                        )
                    
                    # Check format
                    if img.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']:
                        raise serializers.ValidationError(
                            f"Unsupported image format '{img.format}'. "
                            f"Please use JPEG, PNG, GIF, BMP, or WebP format."
                        )
        
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            else:
                # Handle PIL errors and other exceptions
                error_msg = str(e).lower()
                
                if 'cannot identify image file' in error_msg:
                    raise serializers.ValidationError(
                        "Invalid image file. The file appears to be corrupted or is not a valid image format."
                    )
                elif 'truncated' in error_msg or 'incomplete' in error_msg:
                    raise serializers.ValidationError(
                        "Incomplete image file. The image appears to be corrupted or truncated."
                    )
                elif 'decoder' in error_msg:
                    raise serializers.ValidationError(
                        "Image decoding error. The image format may be corrupted or unsupported."
                    )
                else:
                    raise serializers.ValidationError(
                        f"Image validation failed: {str(e)}. "
                        f"Please ensure you're uploading a valid image file."
                    )
        
        finally:
            # Always reset file pointer
            value.seek(0)
        
        return value
    
    def get_is_liked(self, obj):
        """Check if current user has liked this artwork"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by_user(request.user)
        return False
    
    def get_has_duplicates(self, obj):
        """Check if this artwork has potential duplicates"""
        if not obj.perceptual_hash:
            return False
        duplicates = obj.check_for_duplicates(similarity_threshold=5)
        return len(duplicates) > 0
    
    def create(self, validated_data):
        validated_data['artist'] = self.context['request'].user
        return super().create(validated_data)


# Alternative: Add custom validation method to your existing model
# Add this method to your Artwork model in api/models.py

def clean_image_field(self):
    """
    Custom clean method for image field - add this to your Artwork model
    """
    if not self.image:
        return
    
    try:
        # Validate image using PIL
        with Image.open(self.image) as img:
            # Check if image is valid
            img.verify()
            
            # Reset file pointer
            self.image.seek(0)
            
            # Re-open to check properties
            with Image.open(self.image) as img:
                width, height = img.size
                
                # Check dimensions
                if width < 100 or height < 100:
                    raise ValidationError(
                        f"Image too small. Minimum size is 100x100 pixels. "
                        f"Current size: {width}x{height} pixels."
                    )
                
                # Check file size
                if self.image.size > 5 * 1024 * 1024:  # 5MB
                    raise ValidationError(
                        f"Image file too large. Maximum size is 5MB. "
                        f"Current size: {self.image.size/1024/1024:.1f}MB."
                    )
    
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")
    
    finally:
        # Reset file pointer
        if hasattr(self.image, 'seek'):
            self.image.seek(0)


# Usage instructions:
"""
To use the improved validation:

1. Replace your existing ArtworkSerializer with ImprovedArtworkSerializer
2. Or add the clean_image_field method to your Artwork model
3. Update your views.py to use the new serializer

In your views.py, update the ArtworkViewSet:

class ArtworkViewSet(ModelViewSet):
    serializer_class = ImprovedArtworkSerializer  # Use the improved serializer
    # ... rest of your viewset code
"""