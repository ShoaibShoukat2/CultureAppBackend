"""
Test script to verify AWS S3 and Rekognition connectivity
Run this script to ensure your AWS credentials are configured correctly
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.aws_services.s3_storage import S3StorageService
from api.aws_services.rekognition_service import RekognitionService
from django.conf import settings


def test_aws_credentials():
    """Test if AWS credentials are configured"""
    print("=" * 60)
    print("Testing AWS Credentials Configuration")
    print("=" * 60)
    
    required_settings = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME'
    ]
    
    missing = []
    for setting in required_settings:
        value = getattr(settings, setting, None)
        if not value or value == f'your_{setting.lower()}_here':
            missing.append(setting)
            print(f"❌ {setting}: NOT CONFIGURED")
        else:
            # Mask sensitive data
            if 'KEY' in setting:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
                print(f"✅ {setting}: {masked}")
            else:
                print(f"✅ {setting}: {value}")
    
    if missing:
        print("\n⚠️  Missing configuration:")
        print("Please update your .env file with the following:")
        for setting in missing:
            print(f"   {setting}=your_value_here")
        return False
    
    print("\n✅ All AWS credentials are configured!")
    return True


def test_s3_connection():
    """Test S3 connection"""
    print("\n" + "=" * 60)
    print("Testing S3 Connection")
    print("=" * 60)
    
    try:
        s3_service = S3StorageService()
        
        # Try to list objects in bucket (this will fail if bucket doesn't exist or no permissions)
        try:
            response = s3_service.s3_client.list_objects_v2(
                Bucket=s3_service.bucket_name,
                MaxKeys=1
            )
            print(f"✅ Successfully connected to S3 bucket: {s3_service.bucket_name}")
            print(f"✅ Region: {s3_service.region}")
            
            # Check if bucket has any objects
            if 'Contents' in response:
                print(f"✅ Bucket contains {len(response.get('Contents', []))} object(s)")
            else:
                print("ℹ️  Bucket is empty (this is normal for new setup)")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if 'NoSuchBucket' in error_msg:
                print(f"❌ Bucket '{s3_service.bucket_name}' does not exist")
                print("   Please create the bucket in AWS S3 Console")
            elif 'AccessDenied' in error_msg or 'InvalidAccessKeyId' in error_msg:
                print("❌ Access denied - check your AWS credentials")
                print("   Ensure IAM user has S3 permissions")
            else:
                print(f"❌ S3 connection failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize S3 service: {e}")
        return False


def test_rekognition_connection():
    """Test Rekognition connection"""
    print("\n" + "=" * 60)
    print("Testing Rekognition Connection")
    print("=" * 60)
    
    try:
        rekognition_service = RekognitionService()
        
        # Try to call Rekognition API (list collections - lightweight operation)
        try:
            response = rekognition_service.rekognition_client.list_collections()
            print("✅ Successfully connected to AWS Rekognition")
            print(f"✅ Region: {rekognition_service.rekognition_client.meta.region_name}")
            
            collections = response.get('CollectionIds', [])
            if collections:
                print(f"ℹ️  Found {len(collections)} Rekognition collection(s)")
            else:
                print("ℹ️  No Rekognition collections (this is normal)")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if 'AccessDenied' in error_msg or 'InvalidAccessKeyId' in error_msg:
                print("❌ Access denied - check your AWS credentials")
                print("   Ensure IAM user has Rekognition permissions")
            elif 'InvalidSignatureException' in error_msg:
                print("❌ Invalid AWS credentials")
                print("   Check your AWS_SECRET_ACCESS_KEY")
            else:
                print(f"❌ Rekognition connection failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize Rekognition service: {e}")
        return False


def print_summary(credentials_ok, s3_ok, rekognition_ok):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    print(f"AWS Credentials: {'✅ PASS' if credentials_ok else '❌ FAIL'}")
    print(f"S3 Connection: {'✅ PASS' if s3_ok else '❌ FAIL'}")
    print(f"Rekognition Connection: {'✅ PASS' if rekognition_ok else '❌ FAIL'}")
    
    if credentials_ok and s3_ok and rekognition_ok:
        print("\n🎉 All tests passed! Your AWS setup is ready.")
        print("\nNext steps:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Start server: python manage.py runserver")
        print("3. Test artwork upload via API")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Update .env file with correct AWS credentials")
        print("2. Create S3 bucket in AWS Console")
        print("3. Verify IAM user has S3 and Rekognition permissions")
        print("4. Check AWS region is correct")


def main():
    """Run all tests"""
    print("\n🔍 AWS S3 & Rekognition Connection Test")
    print("This script will verify your AWS configuration\n")
    
    # Test 1: Credentials
    credentials_ok = test_aws_credentials()
    
    # Test 2: S3 (only if credentials are configured)
    s3_ok = False
    if credentials_ok:
        s3_ok = test_s3_connection()
    else:
        print("\n⏭️  Skipping S3 test (credentials not configured)")
    
    # Test 3: Rekognition (only if credentials are configured)
    rekognition_ok = False
    if credentials_ok:
        rekognition_ok = test_rekognition_connection()
    else:
        print("\n⏭️  Skipping Rekognition test (credentials not configured)")
    
    # Summary
    print_summary(credentials_ok, s3_ok, rekognition_ok)


if __name__ == '__main__':
    main()
