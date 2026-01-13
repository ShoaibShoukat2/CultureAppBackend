#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

import logging
from api.models import Order

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_latest_orders_with_logging():
    """Check latest orders and try to send emails with detailed logging"""
    
    print("📋 Checking Latest Orders with Detailed Logging:")
    print("=" * 60)
    
    # Get recent orders
    recent_orders = Order.objects.order_by('-created_at')[:3]
    
    for order in recent_orders:
        print(f"\n📦 Order #{order.id}:")
        print(f"   Buyer: {order.buyer.username} ({order.buyer.email})")
        print(f"   Created: {order.created_at}")
        print(f"   Status: {order.status}")
        print(f"   Total: PKR{order.total_amount}")
        
        # Try to send email manually with logging
        try:
            from api.email_service import EmailService
            result = EmailService.send_purchase_confirmation(order)
            print(f"   📧 Email Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"   📧 Email Error: {str(e)}")

def test_bidding_notifications():
    """Check bidding notification functionality"""
    print("\n🎯 Testing Bidding Notifications:")
    print("=" * 60)
    
    from api.notifications.utils import send_notification_email
    
    try:
        # Test bidding notification email
        result = send_notification_email(
            subject="Test Bidding Notification",
            message="This is a test bidding notification to verify the system is working.",
            recipient_email="shoaibahmadbhatti6252@gmail.com"
        )
        print("✅ Bidding notification test: SUCCESS")
    except Exception as e:
        print(f"❌ Bidding notification test FAILED: {str(e)}")

if __name__ == "__main__":
    print("🔍 Detailed Email System Check...")
    
    # Check orders with logging
    check_latest_orders_with_logging()
    
    # Test bidding notifications
    test_bidding_notifications()
    
    print("\n" + "=" * 60)
    print("✅ Detailed check completed!")