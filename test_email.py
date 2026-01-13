#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.core.mail import send_mail
from api.models import Order
from api.email_service import EmailService

def test_email_configuration():
    """Test basic email configuration"""
    try:
        result = send_mail(
            subject='Test Email - CultureUp',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shoaibahmadbhatti6252@gmail.com'],
            fail_silently=False
        )
        print(f"✅ Basic email test: {'SUCCESS' if result else 'FAILED'}")
        return result
    except Exception as e:
        print(f"❌ Basic email test FAILED: {str(e)}")
        return False

def test_order_confirmation_email():
    """Test order confirmation email with latest order"""
    try:
        # Get the latest order
        latest_order = Order.objects.order_by('-created_at').first()
        
        if not latest_order:
            print("❌ No orders found in database")
            return False
            
        print(f"📧 Testing order confirmation for Order #{latest_order.id}")
        
        # Test the email service
        result = EmailService.send_purchase_confirmation(latest_order)
        print(f"✅ Order confirmation email: {'SUCCESS' if result else 'FAILED'}")
        return result
        
    except Exception as e:
        print(f"❌ Order confirmation email FAILED: {str(e)}")
        return False

def check_email_settings():
    """Check email configuration"""
    print("📋 Email Configuration:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")

if __name__ == "__main__":
    print("🔍 Testing Email System...")
    print("=" * 50)
    
    # Check configuration
    check_email_settings()
    print()
    
    # Test basic email
    test_email_configuration()
    print()
    
    # Test order confirmation
    test_order_confirmation_email()
    print()
    
    print("=" * 50)
    print("✅ Email testing completed!")