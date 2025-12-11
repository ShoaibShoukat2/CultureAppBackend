"""
AWS Rekognition Service
Handles duplicate artwork detection using image comparison
"""
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from decimal import Decimal


class RekognitionService:
    """
    Service for detecting duplicate artworks using AWS Rekognition
    
    Strategy:
    1. Compare new artwork against all existing artworks in S3
    2. Use Rekognition's compare_faces for similarity detection
    3. Set similarity threshold (e.g., 90%) to detect duplicates
    4. Store comparison results for audit trail
    """
    
    def __init__(self):
        self.rekognition_client = boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Similarity threshold (90% means images are very similar)
        self.similarity_threshold = 90.0
    
    def detect_labels(self, s3_key):
        """
        Detect labels/objects in an artwork using Rekognition
        This helps in content-based comparison
        
        Args:
            s3_key: S3 object key
            
        Returns:
            dict: {
                'success': bool,
                'labels': list of detected labels,
                'error': str (if failed)
            }
        """
        try:
            response = self.rekognition_client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': s3_key
                    }
                },
                MaxLabels=10,
                MinConfidence=70
            )
            
            labels = [
                {
                    'name': label['Name'],
                    'confidence': label['Confidence']
                }
                for label in response['Labels']
            ]
            
            return {
                'success': True,
                'labels': labels
            }
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'labels': []
            }
    
    def compare_images(self, source_s3_key, target_s3_key):
        """
        Compare two images using Rekognition
        
        Args:
            source_s3_key: New artwork S3 key
            target_s3_key: Existing artwork S3 key
            
        Returns:
            dict: {
                'is_duplicate': bool,
                'similarity': float,
                'matched_artwork_key': str,
                'error': str (if failed)
            }
        """
        try:
            response = self.rekognition_client.compare_faces(
                SourceImage={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': source_s3_key
                    }
                },
                TargetImage={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': target_s3_key
                    }
                },
                SimilarityThreshold=self.similarity_threshold
            )
            
            # Check if faces match (for artworks with people)
            if response['FaceMatches']:
                similarity = response['FaceMatches'][0]['Similarity']
                return {
                    'is_duplicate': True,
                    'similarity': float(similarity),
                    'matched_artwork_key': target_s3_key,
                    'match_type': 'face_match'
                }
            
            return {
                'is_duplicate': False,
                'similarity': 0.0,
                'matched_artwork_key': None
            }
            
        except ClientError as e:
            # If compare_faces fails (no faces detected), try label comparison
            return {
                'is_duplicate': False,
                'similarity': 0.0,
                'error': str(e)
            }
    
    def detect_image_similarity_advanced(self, source_s3_key, target_s3_key):
        """
        Advanced image similarity detection using multiple Rekognition features
        Combines label detection and visual similarity
        
        Args:
            source_s3_key: New artwork S3 key
            target_s3_key: Existing artwork S3 key
            
        Returns:
            dict: {
                'is_duplicate': bool,
                'similarity_score': float (0-100),
                'matched_artwork_key': str,
                'details': dict
            }
        """
        try:
            # Step 1: Get labels for both images
            source_labels_result = self.detect_labels(source_s3_key)
            target_labels_result = self.detect_labels(target_s3_key)
            
            if not source_labels_result['success'] or not target_labels_result['success']:
                return {
                    'is_duplicate': False,
                    'similarity_score': 0.0,
                    'error': 'Failed to detect labels'
                }
            
            source_labels = {label['name'] for label in source_labels_result['labels']}
            target_labels = {label['name'] for label in target_labels_result['labels']}
            
            # Calculate label similarity (Jaccard similarity)
            if source_labels and target_labels:
                intersection = len(source_labels.intersection(target_labels))
                union = len(source_labels.union(target_labels))
                label_similarity = (intersection / union) * 100 if union > 0 else 0
            else:
                label_similarity = 0
            
            # Step 2: Try face comparison
            face_comparison = self.compare_images(source_s3_key, target_s3_key)
            face_similarity = face_comparison.get('similarity', 0.0)
            
            # Step 3: Calculate combined similarity score
            # Weight: 60% label similarity + 40% face similarity
            combined_similarity = (label_similarity * 0.6) + (face_similarity * 0.4)
            
            # Determine if duplicate (threshold: 85%)
            is_duplicate = combined_similarity >= 85.0
            
            return {
                'is_duplicate': is_duplicate,
                'similarity_score': round(combined_similarity, 2),
                'matched_artwork_key': target_s3_key if is_duplicate else None,
                'details': {
                    'label_similarity': round(label_similarity, 2),
                    'face_similarity': round(face_similarity, 2),
                    'source_labels': list(source_labels),
                    'target_labels': list(target_labels)
                }
            }
            
        except Exception as e:
            return {
                'is_duplicate': False,
                'similarity_score': 0.0,
                'error': str(e)
            }
    
    def check_duplicate_artwork(self, new_artwork_s3_key, existing_artworks_keys):
        """
        Check if new artwork is a duplicate of any existing artwork
        
        Args:
            new_artwork_s3_key: S3 key of new artwork
            existing_artworks_keys: List of S3 keys of existing artworks
            
        Returns:
            dict: {
                'is_duplicate': bool,
                'duplicate_found': bool,
                'matched_artwork': str (S3 key of matched artwork),
                'similarity_score': float,
                'total_checked': int,
                'details': list of all comparisons
            }
        """
        if not existing_artworks_keys:
            return {
                'is_duplicate': False,
                'duplicate_found': False,
                'matched_artwork': None,
                'similarity_score': 0.0,
                'total_checked': 0,
                'details': []
            }
        
        comparison_results = []
        highest_similarity = 0.0
        matched_artwork = None
        
        # Compare against all existing artworks
        for existing_key in existing_artworks_keys:
            result = self.detect_image_similarity_advanced(
                new_artwork_s3_key,
                existing_key
            )
            
            comparison_results.append({
                'compared_with': existing_key,
                'similarity_score': result.get('similarity_score', 0.0),
                'is_duplicate': result.get('is_duplicate', False)
            })
            
            # Track highest similarity
            if result.get('similarity_score', 0.0) > highest_similarity:
                highest_similarity = result.get('similarity_score', 0.0)
                if result.get('is_duplicate', False):
                    matched_artwork = existing_key
        
        return {
            'is_duplicate': matched_artwork is not None,
            'duplicate_found': matched_artwork is not None,
            'matched_artwork': matched_artwork,
            'similarity_score': highest_similarity,
            'total_checked': len(existing_artworks_keys),
            'details': comparison_results
        }
