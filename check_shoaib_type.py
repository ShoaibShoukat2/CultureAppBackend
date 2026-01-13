#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import CustomUser

def check_shoaib_user_type():
    """Check shoaib user's type and update if needed"""
    
    try:
        user = CustomUser.objects.get(username='shoaib')
        print(f"👤 Current User: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 User Type: {user.user_type}")
        print(f"🆔 User ID: {user.id}")
        print(f"👑 Is Superuser: {user.is_superuser}")
        print(f"👨‍💼 Is Staff: {user.is_staff}")
        
        # Update to admin if not already
        if user.user_type != 'admin':
            print(f"\n🔄 Updating user type from '{user.user_type}' to 'admin'")
            user.user_type = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✅ User updated to admin")
        else:
            print("✅ User is already admin")
            
        return user
        
    except CustomUser.DoesNotExist:
        print("❌ User 'shoaib' not found")
        return None

if __name__ == "__main__":
    print("🔍 Checking Shoaib User Type")
    print("=" * 40)
    
    check_shoaib_user_type()
    
    print("\n" + "=" * 40)
    print("✅ Check completed!")