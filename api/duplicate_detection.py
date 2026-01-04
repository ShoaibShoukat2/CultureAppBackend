import imagehash
from PIL import Image
from django.db.models import Q
from .models import Artwork


def calculate_perceptual_hashes(image_path):
    """
    Calculate perceptual hashes for an image
    Returns: dict with phash, ahash, dhash
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate different types of perceptual hashes
            phash = str(imagehash.phash(img))
            ahash = str(imagehash.average_hash(img))
            dhash = str(imagehash.dhash(img))
            
            return {
                'phash': phash,
                'ahash': ahash,
                'dhash': dhash
            }
    except Exception as e:
        print(f"Error calculating hashes: {e}")
        return None


def hamming_distance(hash1, hash2):
    """
    Calculate Hamming distance between two hashes
    Lower distance = more similar images
    """
    if not hash1 or not hash2 or len(hash1) != len(hash2):
        return float('inf')
    
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))


def find_duplicate_artworks(new_artwork, similarity_threshold=10):
    """
    Find potential duplicate artworks using perceptual hashing
    
    Args:
        new_artwork: Artwork instance with calculated hashes
        similarity_threshold: Maximum Hamming distance to consider as duplicate (default: 10)
    
    Returns:
        list of tuples: [(artwork, similarity_score, hash_type), ...]
    """
    if not (new_artwork.phash and new_artwork.ahash and new_artwork.dhash):
        return []
    
    # Get all other artworks (exclude the current one and same artist's artworks)
    other_artworks = Artwork.objects.filter(
        duplicate_checked=True
    ).exclude(
        Q(id=new_artwork.id) | Q(artist=new_artwork.artist)
    ).exclude(
        Q(phash__isnull=True) | Q(ahash__isnull=True) | Q(dhash__isnull=True)
    )
    
    duplicates = []
    
    for artwork in other_artworks:
        # Calculate similarity for each hash type
        phash_distance = hamming_distance(new_artwork.phash, artwork.phash)
        ahash_distance = hamming_distance(new_artwork.ahash, artwork.ahash)
        dhash_distance = hamming_distance(new_artwork.dhash, artwork.dhash)
        
        # Use the minimum distance (most similar hash)
        min_distance = min(phash_distance, ahash_distance, dhash_distance)
        
        # Determine which hash type gave the best match
        if min_distance == phash_distance:
            hash_type = 'phash'
        elif min_distance == ahash_distance:
            hash_type = 'ahash'
        else:
            hash_type = 'dhash'
        
        # If similarity is above threshold, consider it a potential duplicate
        if min_distance <= similarity_threshold:
            similarity_percentage = max(0, 100 - (min_distance * 100 / 64))  # Convert to percentage
            duplicates.append((artwork, similarity_percentage, hash_type))
    
    # Sort by similarity (highest first)
    duplicates.sort(key=lambda x: x[1], reverse=True)
    
    return duplicates


def check_artwork_duplicates(artwork):
    """
    Complete duplicate checking workflow for an artwork
    
    Returns:
        dict: {
            'has_duplicates': bool,
            'duplicates': list,
            'message': str
        }
    """
    # Calculate hashes if not already done
    if not artwork.phash:
        hashes = calculate_perceptual_hashes(artwork.image.path)
        if hashes:
            artwork.phash = hashes['phash']
            artwork.ahash = hashes['ahash']
            artwork.dhash = hashes['dhash']
            artwork.duplicate_checked = True
            artwork.save()
        else:
            return {
                'has_duplicates': False,
                'duplicates': [],
                'message': 'Could not calculate image hashes'
            }
    
    # Find duplicates
    duplicates = find_duplicate_artworks(artwork)
    
    if duplicates:
        duplicate_info = []
        for dup_artwork, similarity, hash_type in duplicates:
            duplicate_info.append({
                'artwork_id': dup_artwork.id,
                'title': dup_artwork.title,
                'artist': dup_artwork.artist.username,
                'similarity_percentage': round(similarity, 2),
                'hash_type': hash_type,
                'image_url': dup_artwork.image.url if dup_artwork.image else None
            })
        
        return {
            'has_duplicates': True,
            'duplicates': duplicate_info,
            'message': f'Found {len(duplicates)} potential duplicate(s)'
        }
    else:
        return {
            'has_duplicates': False,
            'duplicates': [],
            'message': 'No duplicates found'
        }


def get_similarity_level(percentage):
    """
    Get human-readable similarity level
    """
    if percentage >= 95:
        return 'Very High (Likely identical)'
    elif percentage >= 85:
        return 'High (Very similar)'
    elif percentage >= 75:
        return 'Medium (Similar)'
    elif percentage >= 65:
        return 'Low (Somewhat similar)'
    else:
        return 'Very Low (Different)'