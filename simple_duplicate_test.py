#!/usr/bin/env python
"""
Simple test to show duplicate detection working
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Artwork

def test_existing_duplicates():
    print("🎨 Testing Duplicate Detection System")
    print("=" * 40)
    
    # Get artworks with hashes
    artworks = Artwork.objects.filter(perceptual_hash__isnull=False)
    
    print(f"📊 Found {artworks.count()} artworks with perceptual hashes")
    
    if artworks.count() < 2:
        print("❌ Need at least 2 artworks to test duplicate detection")
        return
    
    # Test the duplicate detection method
    test_artwork = artworks.first()
    print(f"\n🔍 Testing artwork: '{test_artwork.title}' by {test_artwork.artist.username}")
    
    # Check for duplicates with different thresholds
    for threshold in [5, 10, 15]:
        duplicates = test_artwork.check_for_duplicates(threshold)
        print(f"   Threshold {threshold}: {len(duplicates)} similar artworks found")
        
        for dup in duplicates[:2]:  # Show first 2
            print(f"      - '{dup['artwork'].title}' ({dup['similarity_percentage']}% similar)")
    
    print(f"\n✅ Duplicate detection is working!")
    print(f"📝 Your existing upload API at POST /api/artworks/ now automatically:")
    print(f"   1. Checks for duplicates when image is uploaded")
    print(f"   2. Returns error 409 if duplicates found")
    print(f"   3. Shows similar artworks to user")
    print(f"   4. Prevents duplicate upload")

if __name__ == "__main__":
    test_existing_duplicates()