#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Order, CustomUser
from api.signals import send_order_confirmation_email
from django.db.models.signals import post_save

def check_recent_orders():
    """Check recent orders and their email status"""
    print("📋 Recent Orders:")
    orders = Order.objects.order_by('-created_at')[:5]
    
    for order in orders:
        print(f"   Order #{order.id} - {order.buyer.username} - {order.created_at} - Status: {order.status}")
    
    return orders

def test_signal_manually():
    """Test the signal manually"""
    try:
        latest_order = Order.objects.order_by('-created_at').first()
        if latest_order:
            print(f"\n🔧 Testing signal manually for Order #{latest_order.id}")
            
            # Call the signal function directly
            send_order_confirmation_email(
                sender=Order,
                instance=latest_order,
                created=True
            )
            print("✅ Signal executed successfully")
        else:
            print("❌ No orders found")
    except Exception as e:
        print(f"❌ Signal test failed: {str(e)}")

def check_signal_connections():
    """Check if signals are properly connected"""
    print("\n🔗 Checking Signal Connections:")
    
    # Get all connected signals for Order model
    receivers = post_save._live_receivers(sender=Order)
    print(f"   post_save signals for Order model: {len(receivers)} connected")
    
    for receiver in receivers:
        if hasattr(receiver, '__name__'):
            print(f"   - {receiver.__name__}")
        else:
            print(f"   - {receiver}")

def create_test_order():
    """Create a test order to trigger the signal"""
    try:
        # Get a user to create order for
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found to create test order")
            return
            
        print(f"\n🆕 Creating test order for user: {user.username}")
        
        # Create a new order (this should trigger the signal)
        order = Order.objects.create(
            buyer=user,
            order_type='artwork',
            status='pending',
            total_amount=100.00,
            shipping_address="Test Address, Test City"
        )
        
        print(f"✅ Test order created: #{order.id}")
        print("📧 Signal should have been triggered automatically")
        
    except Exception as e:
        print(f"❌ Failed to create test order: {str(e)}")

if __name__ == "__main__":
    print("🔍 Debugging Email Signals...")
    print("=" * 50)
    
    # Check recent orders
    check_recent_orders()
    
    # Check signal connections
    check_signal_connections()
    
    # Test signal manually
    test_signal_manually()
    
    # Create test order
    create_test_order()
    
    print("\n" + "=" * 50)
    print("✅ Signal debugging completed!")