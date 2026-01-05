"""
Configuration settings for duplicate detection system
"""

# Duplicate detection thresholds
DUPLICATE_DETECTION_CONFIG = {
    # Similarity threshold above which uploads are blocked (percentage)
    'BLOCK_THRESHOLD': 85.0,
    
    # Similarity threshold for showing warnings (percentage)
    'WARNING_THRESHOLD': 70.0,
    
    # Hamming distance threshold for duplicate detection (lower = more similar)
    'HAMMING_DISTANCE_THRESHOLD': 10,
    
    # Whether to enable duplicate blocking (if False, only shows warnings)
    'ENABLE_BLOCKING': True,
    
    # Whether to check duplicates on artwork updates
    'CHECK_ON_UPDATE': True,
    
    # Whether to allow same artist to upload similar artworks
    'ALLOW_SAME_ARTIST_DUPLICATES': True,
}

def get_duplicate_config():
    """Get duplicate detection configuration"""
    return DUPLICATE_DETECTION_CONFIG

def is_duplicate_blocking_enabled():
    """Check if duplicate blocking is enabled"""
    return DUPLICATE_DETECTION_CONFIG.get('ENABLE_BLOCKING', True)

def get_block_threshold():
    """Get the similarity threshold for blocking uploads"""
    return DUPLICATE_DETECTION_CONFIG.get('BLOCK_THRESHOLD', 85.0)

def get_warning_threshold():
    """Get the similarity threshold for showing warnings"""
    return DUPLICATE_DETECTION_CONFIG.get('WARNING_THRESHOLD', 70.0)

def get_hamming_threshold():
    """Get the Hamming distance threshold"""
    return DUPLICATE_DETECTION_CONFIG.get('HAMMING_DISTANCE_THRESHOLD', 10)