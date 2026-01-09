#!/usr/bin/env python3
"""
Test the new like functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Artwork, Category, ArtworkLike
from PIL import Image
import tempfile

User = get_user_model()

def create_test_image(filename):
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), (255, 0, 0))
    img.save(filename, 'JPEG')
    return filename

def test_like_functionality():
    """Test the like functionality"""
    print("🧪 Testing Like Functionality\n")
    
    # Create test users
    try:
        artist = User.objects.get(username='test_like_artist')
    except User.DoesNotExist:
        artist = User.objects.create_user(
            username='test_like_artist',
            email='artist@like.com',
            password='testpass123',
            user_type='artist'
        )
    
    try:
        user1 = User.objects.get(username='test_like_user1')
    except User.DoesNotExist:
        user1 = User.objects.create_user(
            username='test_like_user1',
            email='user1@like.com',
            password='testpass123',
            user_type='buyer'
        )
    
    try:
        user2 = User.objects.get(username='test_like_user2')
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username='test_like_user2',
            email='user2@like.com',
            password='testpass123',
            user_type='buyer'
        )
    
    # Create category
    category, _ = Category.objects.get_or_create(
        name='Like Test Category',
        defaults={'description': 'Test category for like functionality'}
    )
    
    # Create artwork
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        create_test_image(tmp.name)
        
        artwork = Artwork.objects.create(
            artist=artist,
            title='Test Artwork for Likes',
            description='Artwork to test like functionality',
            category=category,
            artwork_type='digital',
            price=100.00
        )
        
        with open(tmp.name, 'rb') as f:
            artwork.image.save('test_like.jpg', f, save=True)
        
        print(f"✅ Created artwork: {artwork.title}")
        print(f"   Initial likes count: {artwork.likes_count}")
        print(f"   Initial likes from model: {artwork.get_likes_count()}")
        
        # Test 1: User1 likes the artwork
        print("\n📤 Test 1: User1 likes the artwork")
        liked, likes_count = artwork.toggle_like(user1)
        print(f"   Result: liked={liked}, likes_count={likes_count}")
        print(f"   Is liked by user1: {artwork.is_liked_by_user(user1)}")
        print(f"   Is liked by user2: {artwork.is_liked_by_user(user2)}")
        
        # Test 2: User2 likes the artwork
        print("\n📤 Test 2: User2 likes the artwork")
        liked, likes_count = artwork.toggle_like(user2)
        print(f"   Result: liked={liked}, likes_count={likes_count}")
        print(f"   Is liked by user1: {artwork.is_liked_by_user(user1)}")
        print(f"   Is liked by user2: {artwork.is_liked_by_user(user2)}")
        
        # Test 3: User1 tries to like again (should unlike)
        print("\n📤 Test 3: User1 tries to like again (should unlike)")
        liked, likes_count = artwork.toggle_like(user1)
        print(f"   Result: liked={liked}, likes_count={likes_count}")
        print(f"   Is liked by user1: {artwork.is_liked_by_user(user1)}")
        print(f"   Is liked by user2: {artwork.is_liked_by_user(user2)}")
        
        # Test 4: User1 likes again
        print("\n📤 Test 4: User1 likes again")
        liked, likes_count = artwork.toggle_like(user1)
        print(f"   Result: liked={liked}, likes_count={likes_count}")
        print(f"   Is liked by user1: {artwork.is_liked_by_user(user1)}")
        print(f"   Is liked by user2: {artwork.is_liked_by_user(user2)}")
        
        # Test 5: Check database consistency
        print("\n📊 Test 5: Database consistency check")
        db_likes_count = ArtworkLike.objects.filter(artwork=artwork).count()
        model_likes_count = artwork.get_likes_count()
        artwork_likes_count = artwork.likes_count
        
        print(f"   Database ArtworkLike count: {db_likes_count}")
        print(f"   Model get_likes_count(): {model_likes_count}")
        print(f"   Artwork.likes_count field: {artwork_likes_count}")
        
        if db_likes_count == model_likes_count == artwork_likes_count:
            print("   ✅ All counts match - consistency maintained!")
        else:
            print("   ❌ Counts don't match - inconsistency detected!")
        
        # Test 6: Get all users who liked
        print("\n👥 Test 6: Users who liked this artwork")
        likes = ArtworkLike.objects.filter(artwork=artwork).select_related('user')
        for like in likes:
            print(f"   - {like.user.username} liked at {like.created_at}")
        
        # Cleanup
        artwork.delete()
        os.unlink(tmp.name)
        
        print("\n✅ Like functionality test completed!")
        return True

def main():
    """Run the test"""
    print("🚀 Testing Like Functionality\n")
    
    try:
        test_like_functionality()
        print("\n🎉 All like tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()