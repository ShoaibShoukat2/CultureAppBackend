# 🎨 Artwork Duplicate Detection System

## Overview

This system uses **Perceptual Hashing** to detect duplicate artworks automatically. It prevents artists from uploading duplicate or very similar images, ensuring originality on your platform.

## ✨ Features

- **Automatic Detection**: Checks for duplicates during artwork upload
- **Perceptual Hashing**: Detects duplicates even with minor modifications (resize, compression, slight color changes)
- **Configurable Sensitivity**: Adjust similarity thresholds based on your needs
- **API Endpoints**: Multiple ways to check and manage duplicates
- **Management Commands**: Tools for administrators to find and manage duplicates

## 🔧 How It Works

### Perceptual Hashing Algorithm
- Uses **Average Hash (aHash)** with 16x16 hash size
- Creates a 64-bit "fingerprint" for each image
- Compares fingerprints using Hamming distance
- Lower distance = more similar images

### Similarity Thresholds
- **0-2**: Extremely strict (only catches exact duplicates)
- **3-5**: Strict (recommended for duplicate prevention)
- **6-10**: Moderate (catches similar compositions)
- **11-15**: Lenient (catches loosely similar images)
- **16+**: Very lenient (may catch false positives)

## 🚀 API Endpoints

### 1. Upload Artwork (with duplicate detection)
```http
POST /api/artworks/
Content-Type: multipart/form-data

{
    "title": "My Artwork",
    "description": "Beautiful painting",
    "category_id": 1,
    "price": 100.00,
    "image": [file]
}
```

**Response if duplicates found:**
```json
{
    "error": "Duplicate artwork detected",
    "message": "This image appears to be very similar to existing artworks.",
    "duplicate_count": 2,
    "similar_artworks": [
        {
            "artwork_id": 15,
            "title": "Similar Painting",
            "artist": "other_artist",
            "similarity_percentage": 95.3,
            "upload_date": "2025-01-10",
            "image_url": "/media/artworks/similar.jpg"
        }
    ],
    "action_required": "Please choose a different image or confirm this is your original work"
}
```

### 2. Check for Duplicates Before Upload
```http
POST /api/artworks/check_duplicate/
Content-Type: multipart/form-data

{
    "image": [file],
    "similarity_threshold": 5  // optional, default: 5
}
```

**Response:**
```json
{
    "is_duplicate": true,
    "duplicate_count": 1,
    "similar_artworks": [...],
    "message": "Found 1 similar artwork(s)",
    "recommendation": "Consider uploading original content only"
}
```

### 3. Force Upload (bypass duplicate check)
```http
POST /api/artworks/force_upload/
Content-Type: multipart/form-data

{
    "title": "My Artwork",
    "description": "I confirm this is original",
    "category_id": 1,
    "price": 100.00,
    "image": [file],
    "confirm_duplicate_upload": true
}
```

### 4. Find Similar Artworks
```http
GET /api/artworks/{id}/find_similar/?threshold=10
```

**Response:**
```json
{
    "artwork_id": 15,
    "artwork_title": "My Painting",
    "similar_count": 2,
    "similar_artworks": [
        {
            "artwork": {...},
            "similarity_percentage": 87.5,
            "similarity_score": 8
        }
    ],
    "threshold_used": 10
}
```

## 🛠️ Management Commands

### Generate Hashes for Existing Artworks
```bash
# Generate hashes for artworks without them
python manage.py generate_artwork_hashes

# Regenerate all hashes (force mode)
python manage.py generate_artwork_hashes --force
```

### Find and Manage Duplicates
```bash
# Find duplicates with default threshold (5)
python manage.py find_duplicates

# Find duplicates with custom threshold
python manage.py find_duplicates --threshold 8

# Find and delete duplicates (keeps oldest)
python manage.py find_duplicates --delete-duplicates --threshold 5
```

## 📱 Frontend Integration

### Upload Flow with Duplicate Check

```javascript
// 1. Check for duplicates first
const checkDuplicate = async (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/api/artworks/check_duplicate/', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${userToken}`
        },
        body: formData
    });
    
    return response.json();
};

// 2. Handle upload based on duplicate check
const uploadArtwork = async (artworkData, imageFile) => {
    // Check for duplicates first
    const duplicateCheck = await checkDuplicate(imageFile);
    
    if (duplicateCheck.is_duplicate) {
        // Show warning to user
        const userConfirms = confirm(
            `Found ${duplicateCheck.duplicate_count} similar artworks. ` +
            `Are you sure this is your original work?`
        );
        
        if (!userConfirms) {
            return { cancelled: true };
        }
        
        // Use force upload if user confirms
        artworkData.confirm_duplicate_upload = true;
        return forceUpload(artworkData);
    } else {
        // Normal upload
        return normalUpload(artworkData);
    }
};
```

### Display Duplicate Warnings

```javascript
// Show duplicate warning in UI
const showDuplicateWarning = (duplicates) => {
    const warningHtml = `
        <div class="duplicate-warning">
            <h3>⚠️ Similar Artworks Found</h3>
            <p>We found ${duplicates.length} similar artworks:</p>
            <div class="similar-artworks">
                ${duplicates.map(dup => `
                    <div class="similar-artwork">
                        <img src="${dup.image_url}" alt="${dup.title}">
                        <p><strong>${dup.title}</strong> by ${dup.artist}</p>
                        <p>Similarity: ${dup.similarity_percentage}%</p>
                    </div>
                `).join('')}
            </div>
            <p>Please ensure you're uploading original content only.</p>
        </div>
    `;
    
    document.getElementById('duplicate-warning').innerHTML = warningHtml;
};
```

## ⚙️ Configuration

### Adjust Similarity Thresholds

In your views or settings:

```python
# Strict duplicate detection (recommended)
DUPLICATE_THRESHOLD_STRICT = 3

# Moderate duplicate detection
DUPLICATE_THRESHOLD_MODERATE = 8

# Lenient duplicate detection
DUPLICATE_THRESHOLD_LENIENT = 15

# Use in views
duplicates = Artwork.find_duplicates_for_image(
    image_file, 
    similarity_threshold=DUPLICATE_THRESHOLD_STRICT
)
```

### Database Indexing

The `perceptual_hash` field is indexed for fast lookups:

```python
# In models.py
perceptual_hash = models.CharField(
    max_length=64, 
    blank=True, 
    null=True, 
    db_index=True  # Fast lookups
)
```

## 🔍 Testing

Run the test script to verify everything works:

```bash
python test_duplicate_detection.py
```

## 📊 Performance Considerations

### Hash Generation
- **Time**: ~50-200ms per image (depending on size)
- **Storage**: 64 characters per artwork
- **Memory**: Minimal impact

### Duplicate Checking
- **Time**: ~1-5ms per comparison
- **Scalability**: Linear with number of artworks
- **Optimization**: Database indexing on hash field

### Recommendations
- Generate hashes asynchronously for large images
- Consider caching for frequently accessed comparisons
- Monitor database performance with large datasets

## 🛡️ Security & Privacy

- Hashes are one-way (cannot reconstruct image)
- No sensitive data stored in hashes
- Comparison happens server-side only
- Original images remain secure

## 🎯 Best Practices

1. **Set appropriate thresholds**: Start with 5, adjust based on false positives
2. **User education**: Explain why duplicates are blocked
3. **Allow appeals**: Provide force upload for legitimate cases
4. **Regular cleanup**: Use management commands to find duplicates
5. **Monitor performance**: Watch database query times

## 🚨 Troubleshooting

### Common Issues

**Hash generation fails:**
```bash
# Check if imagehash is installed
pip install imagehash

# Verify image files exist
python manage.py generate_artwork_hashes --force
```

**Too many false positives:**
```python
# Increase threshold (less strict)
similarity_threshold = 8  # instead of 5
```

**Too few duplicates caught:**
```python
# Decrease threshold (more strict)
similarity_threshold = 3  # instead of 5
```

**Performance issues:**
```sql
-- Check if index exists
SHOW INDEX FROM api_artwork WHERE Column_name = 'perceptual_hash';

-- Add index if missing
CREATE INDEX idx_perceptual_hash ON api_artwork(perceptual_hash);
```

## 📈 Monitoring

Track duplicate detection effectiveness:

```python
# In your analytics
duplicate_blocks = ArtworkUploadAttempt.objects.filter(
    blocked_reason='duplicate'
).count()

false_positives = ArtworkUploadAttempt.objects.filter(
    blocked_reason='duplicate',
    force_uploaded=True
).count()

effectiveness_rate = (duplicate_blocks - false_positives) / duplicate_blocks * 100
```

---

## 🎉 Conclusion

This duplicate detection system provides robust protection against duplicate uploads while maintaining good user experience. The perceptual hashing approach is industry-standard and highly effective for image similarity detection.

**Key Benefits:**
- ✅ Prevents duplicate content
- ✅ Maintains platform quality
- ✅ Fast and efficient
- ✅ Configurable sensitivity
- ✅ User-friendly warnings
- ✅ Administrative tools included

The system is now ready for production use! 🚀