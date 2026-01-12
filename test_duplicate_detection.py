#!/usr/bin/env python
"""
Test script for duplicate artwork detection
Run this after setting up the duplicate detection system
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Artwork, CustomUser
from PIL import Image
import imagehash

def test_duplicate_detection():
    print("🎨 Testing Duplicate Artwork Detection System")
    print("=" * 50)
    
    # Get some existing artworks
    artworks = Artwork.objects.filter(perceptual_hash__isnull=False)[:5]
    
    if not artworks:
        print("❌ No artworks with perceptual hashes found.")
        print("   Run: python manage.py generate_artwork_hashes")
        return
    
    print(f"📊 Found {artworks.count()} artworks with perceptual hashes")
    print()
    
    # Test 1: Check for duplicates in existing artworks
    print("🔍 Test 1: Checking existing artworks for duplicates")
    print("-" * 40)
    
    for artwork in artworks:
        duplicates = artwork.check_for_duplicates(similarity_threshold=5)
        if duplicates:
            print(f"⚠️  Artwork '{artwork.title}' has {len(duplicates)} potential duplicates:")
            for dup in duplicates[:2]:  # Show top 2
                print(f"   - '{dup['artwork'].title}' by {dup['artwork'].artist.username}")
                print(f"     Similarity: {dup['similarity_percentage']}%")
        else:
            print(f"✅ Artwork '{artwork.title}' - No duplicates found")
    
    print()
    
    # Test 2: Demonstrate hash generation
    print("🔍 Test 2: Demonstrating hash generation")
    print("-" * 40)
    
    for artwork in artworks[:3]:
        if artwork.image:
            try:
                print(f"📷 Artwork: {artwork.title}")
                print(f"   Hash: {artwork.perceptual_hash}")
                print(f"   Artist: {artwork.artist.username}")
                print(f"   Upload Date: {artwork.created_at.strftime('%Y-%m-%d')}")
                print()
            except Exception as e:
                print(f"❌ Error processing {artwork.title}: {e}")
    
    # Test 3: Show similarity thresholds
    print("🔍 Test 3: Different similarity thresholds")
    print("-" * 40)
    
    if artworks:
        test_artwork = artworks[0]
        print(f"Testing artwork: '{test_artwork.title}'")
        
        for threshold in [3, 5, 10, 15]:
            duplicates = test_artwork.check_for_duplicates(threshold)
            print(f"   Threshold {threshold}: {len(duplicates)} similar artworks")
    
    print()
    print("🎯 Duplicate Detection System Test Complete!")
    print()
    print("📝 How to use:")
    print("   1. Upload artwork via API - duplicates are automatically detected")
    print("   2. Use /api/artworks/check_duplicate/ to check before uploading")
    print("   3. Use /api/artworks/{id}/find_similar/ to find similar artworks")
    print("   4. Adjust similarity_threshold (1-64): lower = stricter")

if __name__ == "__main__":
    test_duplicate_detection()