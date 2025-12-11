"""
AWS S3 Storage Service
Handles uploading, retrieving, and deleting artwork images from S3
"""
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
import os
from io import BytesIO


class S3StorageService:
    """Service for managing artwork images in AWS S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region = settings.AWS_S3_REGION_NAME
    
    def generate_unique_filename(self, original_filename, artist_id):
        """
        Generate a unique filename for S3 storage
        Format: artworks/{artist_id}/{uuid}_{original_filename}
        """
        ext = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"artworks/{artist_id}/{unique_id}{ext}"
    
    def upload_artwork(self, file_obj, artist_id, original_filename):
        """
        Upload artwork image to S3
        
        Args:
            file_obj: File object (from request.FILES)
            artist_id: ID of the artist uploading
            original_filename: Original filename
            
        Returns:
            dict: {
                'success': bool,
                's3_key': str,
                's3_url': str,
                'error': str (if failed)
            }
        """
        try:
            # Generate unique filename
            s3_key = self.generate_unique_filename(original_filename, artist_id)
            
            # Read file content
            file_content = file_obj.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file_obj.content_type,
                Metadata={
                    'artist_id': str(artist_id),
                    'original_filename': original_filename
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            return {
                'success': True,
                's3_key': s3_key,
                's3_url': s3_url
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_artwork(self, s3_key):
        """
        Delete artwork from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            dict: {'success': bool, 'error': str (if failed)}
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return {'success': True}
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_artwork_url(self, s3_key):
        """
        Get public URL for artwork
        
        Args:
            s3_key: S3 object key
            
        Returns:
            str: Public URL
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def get_artwork_bytes(self, s3_key):
        """
        Get artwork image bytes from S3 (for Rekognition)
        
        Args:
            s3_key: S3 object key
            
        Returns:
            bytes: Image bytes or None if error
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error getting artwork bytes: {e}")
            return None
    
    def list_artist_artworks(self, artist_id):
        """
        List all artworks for a specific artist
        
        Args:
            artist_id: Artist ID
            
        Returns:
            list: List of S3 keys
        """
        try:
            prefix = f"artworks/{artist_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except ClientError as e:
            print(f"Error listing artworks: {e}")
            return []
