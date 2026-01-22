#!/usr/bin/env python
"""
Test script to verify stock management fixes
Run this after implementing the fixes to test the functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Equipment, Order, Payment, EquipmentOrderItem, CustomUser
from decimal import Decimal

def test_stock_management():
    """Test stock management functionality"""
    
    print("🧪 Testing Stock Management System...")
    print("=" * 50)
    
    # 1. Check current equipment stock
    print("\n1. Current Equipment Stock:")
    equipment_list = Equipment.objects.all()
    for eq in equipment_list[:5]:  # Show first 5
        print(f"   {eq.name}: {eq.stock_quantity} units (Available: {eq.is_available})")
    
    # 2. Check orders vs payments mismatch
    total_orders = Order.objects.count()
    total_payments = Payment.objects.count()
    order_payments = Payment.objects.filter(order__isnull=False).count()
    job_payments = Payment.objects.filter(job__isnull=False).count()
    
    print(f"\n2. Orders vs Payments Analysis:")
    print(f"   Total Orders: {total_orders}")
    print(f"   Total Payments: {total_payments}")
    print(f"   Order Payments: {order_payments}")
    print(f"   Job Payments: {job_payments}")
    print(f"   Orphan Payments: {total_payments - order_payments - job_payments}")
    
    # 3. Check recent payments
    print(f"\n3. Recent Payments (Last 5):")
    recent_payments = Payment.objects.order_by('-created_at')[:5]
    for payment in recent_payments:
        payment_type = "Order" if payment.order else "Job" if payment.job else "Unknown"
        print(f"   {payment.transaction_id}: PKR{payment.amount} ({payment_type}) - {payment.status}")
    
    # 4. Check equipment with low stock
    print(f"\n4. Equipment with Low Stock (< 5 units):")
    low_stock = Equipment.objects.filter(stock_quantity__lt=5)
    for eq in low_stock:
        print(f"   ⚠️  {eq.name}: {eq.stock_quantity} units")
    
    # 5. Check orders without payments
    print(f"\n5. Orders without Payments:")
    orders_without_payments = Order.objects.filter(buyer_payments__isnull=True)
    print(f"   Orders without payments: {orders_without_payments.count()}")
    
    # 6. Check payments without orders (job payments are normal)
    print(f"\n6. Payments without Orders (Job payments are normal):")
    payments_without_orders = Payment.objects.filter(order__isnull=True, job__isnull=True)
    print(f"   Orphan payments: {payments_without_orders.count()}")
    
    print("\n" + "=" * 50)
    print("✅ Stock Management Test Complete!")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if total_orders == 0 and order_payments == 0:
        print("   🔧 No equipment orders found - users may be bypassing order creation")
    if low_stock.exists():
        print("   📦 Some equipment has low stock - consider restocking")
    if payments_without_orders.filter(job__isnull=True).exists():
        print("   🔍 Found orphan payments - investigate payment flow")

def create_test_order():
    """Create a test order to verify the system works"""
    
    print("\n🧪 Creating Test Order...")
    
    try:
        # Get a test user (buyer)
        buyer = CustomUser.objects.filter(user_type='buyer').first()
        if not buyer:
            print("   ❌ No buyer users found - create a buyer user first")
            return
        
        # Get equipment with stock
        equipment = Equipment.objects.filter(stock_quantity__gt=0).first()
        if not equipment:
            print("   ❌ No equipment with stock found")
            return
        
        print(f"   👤 Buyer: {buyer.username}")
        print(f"   📦 Equipment: {equipment.name} (Stock: {equipment.stock_quantity})")
        
        # Create order
        order = Order.objects.create(
            buyer=buyer,
            order_type='equipment',
            shipping_address='Test Address, Test City',
            status='pending'
        )
        
        # Add equipment item
        order_item = EquipmentOrderItem.objects.create(
            order=order,
            equipment=equipment,
            quantity=1,
            price=equipment.price
        )
        
        # Calculate total
        order.calculate_total()
        
        print(f"   ✅ Test order created: #{order.id}")
        print(f"   💰 Total amount: PKR{order.total_amount}")
        
        # Create payment
        payment = Payment.objects.create(
            payer=buyer,
            order=order,
            amount=order.total_amount,
            payment_method='stripe',
            status='completed'  # Simulate completed payment
        )
        
        print(f"   ✅ Test payment created: {payment.transaction_id}")
        
        # Check if stock was reduced
        equipment.refresh_from_db()
        print(f"   📦 Equipment stock after payment: {equipment.stock_quantity}")
        
        return order, payment
        
    except Exception as e:
        print(f"   ❌ Error creating test order: {str(e)}")
        return None, None

if __name__ == "__main__":
    test_stock_management()
    
    # Uncomment to create test order
    # create_test_order()