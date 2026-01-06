#!/usr/bin/env python3
"""
Test to show the exact response format for duplicate detection
"""
import os
import sys
import django
from PIL import Image, ImageDraw
import tempfile
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Artwork, Category
from api.duplicate_detection import check_artwork_duplicates
from api.serializers import ArtworkSerializer

User = get_user_model()

def create_test_image(filename, color=(255, 0, 0)):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 255, 0))
    img.save(filename, 'JPEG')
    return filename

def simulate_api_response():
    """Simulate what the API response looks like"""
    print("🎯 DUPLICATE DETECTION API RESPONSE EXAMPLES\n")
    
    # Create test users
    try:
        artist1 = User.objects.get(username='response_test1')
    except User.DoesNotExist:
        artist1 = User.objects.create_user(
            username='response_test1',
            email='test1@response.com',
            password='testpass123',
            user_type='artist'
        )
    
    try:
        artist2 = User.objects.get(username='response_test2')
    except User.DoesNotExist:
        artist2 = User.objects.create_user(
            username='response_test2',
            email='test2@response.com',
            password='testpass123',
            user_type='artist'
        )
    
    # Create category
    category, _ = Category.objects.get_or_create(
        name='Response Test Category',
        defaults={'description': 'Test category for response format'}
    )
    
    try:
        # SCENARIO 1: Original artwork (no duplicates)
        print("📤 SCENARIO 1: ORIGINAL ARTWORK UPLOAD")
        print("=" * 60)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp1:
            create_test_image(tmp1.name, (255, 0, 0))
            
            artwork1 = Artwork.objects.create(
                artist=artist1,
                title='Beautiful Landscape',
                description='Original landscape artwork',
                category=category,
                artwork_type='digital',
                price=299.99
            )
            
            with open(tmp1.name, 'rb') as f:
                artwork1.image.save('landscape.jpg', f, save=True)
            
            # Check duplicates
            duplicate_result = check_artwork_duplicates(artwork1)
            
            # Simulate API response
            response1 = {
                'success': True,
                'message': '✅ Artwork uploaded successfully',
                'artwork': {
                    'id': artwork1.id,
                    'title': artwork1.title,
                    'artist': artwork1.artist.username,
                    'price': str(artwork1.price)
                },
                'duplicate_check': duplicate_result,
                'duplicate_detection_status': 'COMPLETED',
                'duplicate_summary': '✅ No similar artworks found - completely original!',
                'duplicate_detection_info': {
                    'checked': True,
                    'threshold_for_blocking': 85.0,
                    'total_artworks_compared': 0,
                    'detection_method': 'Perceptual Hash (pHash + aHash + dHash)'
                }
            }
            
            print("✅ SUCCESS RESPONSE (201 Created):")
            print(json.dumps(response1, indent=2))
            
            os.unlink(tmp1.name)
        
        # SCENARIO 2: Similar artwork (warning but allowed)
        print("\n\n⚠️ SCENARIO 2: SIMILAR ARTWORK (WARNING)")
        print("=" * 60)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp2:
            create_test_image(tmp2.name, (255, 20, 20))  # Slightly different
            
            artwork2 = Artwork.objects.create(
                artist=artist2,
                title='Mountain View',
                description='Similar landscape artwork',
                category=category,
                artwork_type='digital',
                price=250.00
            )
            
            with open(tmp2.name, 'rb') as f:
                artwork2.image.save('mountain.jpg', f, save=True)
            
            # Check duplicates
            duplicate_result2 = check_artwork_duplicates(artwork2)
            
            # Simulate response with warning
            if duplicate_result2['has_duplicates']:
                response2 = {
                    'success': True,
                    'message': '✅ Artwork uploaded successfully',
                    'artwork': {
                        'id': artwork2.id,
                        'title': artwork2.title,
                        'artist': artwork2.artist.username,
                        'price': str(artwork2.price)
                    },
                    'duplicate_check': duplicate_result2,
                    'duplicate_detection_status': 'COMPLETED',
                    'warning': '⚠️ SIMILAR ARTWORKS FOUND (but upload allowed)',
                    'duplicate_details': duplicate_result2['duplicates'],
                    'duplicate_summary': f"🔍 Found {len(duplicate_result2['duplicates'])} similar artwork(s) below blocking threshold",
                    'similarity_details': [
                        f"• '{dup['title']}' by {dup['artist']} - {dup['similarity_percentage']:.1f}% similar"
                        for dup in duplicate_result2['duplicates']
                    ],
                    'duplicate_detection_info': {
                        'checked': True,
                        'threshold_for_blocking': 85.0,
                        'total_artworks_compared': 1,
                        'detection_method': 'Perceptual Hash (pHash + aHash + dHash)'
                    }
                }
                
                print("⚠️ WARNING RESPONSE (201 Created with warnings):")
                print(json.dumps(response2, indent=2))
            
            os.unlink(tmp2.name)
        
        # SCENARIO 3: Duplicate artwork (blocked)
        print("\n\n🚫 SCENARIO 3: DUPLICATE ARTWORK (BLOCKED)")
        print("=" * 60)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp3:
            create_test_image(tmp3.name, (255, 1, 1))  # Almost identical
            
            artwork3 = Artwork.objects.create(
                artist=artist2,
                title='Copied Landscape',
                description='Duplicate landscape artwork',
                category=category,
                artwork_type='digital',
                price=200.00
            )
            
            with open(tmp3.name, 'rb') as f:
                artwork3.image.save('copied.jpg', f, save=True)
            
            # Check duplicates
            duplicate_result3 = check_artwork_duplicates(artwork3)
            
            # Simulate blocked response
            if duplicate_result3['has_duplicates']:
                highest_similarity = max(dup['similarity_percentage'] for dup in duplicate_result3['duplicates'])
                
                if highest_similarity >= 85.0:
                    blocked_response = {
                        'success': False,
                        'error': 'Duplicate artwork detected',
                        'message': f'❌ UPLOAD BLOCKED: This artwork is {highest_similarity:.1f}% similar to existing artwork.',
                        'duplicate_detected': True,
                        'blocked_duplicates': duplicate_result3['duplicates'],
                        'threshold_used': 85.0,
                        'similar_to': {
                            'title': duplicate_result3['duplicates'][0]['title'],
                            'artist': duplicate_result3['duplicates'][0]['artist'],
                            'similarity': f"{duplicate_result3['duplicates'][0]['similarity_percentage']:.1f}%"
                        },
                        'help': '💡 Please upload original artwork or make significant modifications to make it more unique.',
                        'duplicate_info': f"🔍 Found {len(duplicate_result3['duplicates'])} duplicate(s) above 85.0% similarity threshold"
                    }
                    
                    print("🚫 BLOCKED RESPONSE (400 Bad Request):")
                    print(json.dumps(blocked_response, indent=2))
                    
                    # Delete the duplicate (simulate blocking)
                    artwork3.delete()
            
            os.unlink(tmp3.name)
        
        # Cleanup
        artwork1.delete()
        if Artwork.objects.filter(id=artwork2.id).exists():
            artwork2.delete()
        
        print("\n\n📋 SUMMARY:")
        print("=" * 60)
        print("✅ Original artworks: Upload successful with no warnings")
        print("⚠️  Similar artworks: Upload successful with similarity warnings")
        print("🚫 Duplicate artworks: Upload blocked with detailed error message")
        print("\n🔍 All responses include:")
        print("   • duplicate_check: Complete duplicate detection results")
        print("   • duplicate_detection_status: Confirmation that check was completed")
        print("   • duplicate_summary: Human-readable summary")
        print("   • duplicate_detection_info: Technical details about the detection")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    simulate_api_response()