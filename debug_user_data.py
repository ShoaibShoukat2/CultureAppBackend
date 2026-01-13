#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import CustomUser, Order, Payment, Job

def debug_shoaib_data():
    """Debug shoaib user's data in detail"""
    
    try:
        user = CustomUser.objects.get(username='shoaib')
        print(f"👤 User: {user.username} ({user.user_type})")
        print(f"📧 Email: {user.email}")
        print(f"🆔 User ID: {user.id}")
        
        # Check Orders
        print(f"\n📦 ORDERS:")
        orders = user.buyer_orders.all()
        print(f"Total Orders: {orders.count()}")
        
        for order in orders:
            print(f"   Order #{order.id}:")
            print(f"     Status: {order.status}")
            print(f"     Amount: PKR{order.total_amount}")
            print(f"     Created: {order.created_at}")
            
            # Check payments for this order
            order_payments = Payment.objects.filter(order=order)
            print(f"     Payments for this order: {order_payments.count()}")
            
            for payment in order_payments:
                print(f"       Payment {payment.transaction_id}: {payment.status} - PKR{payment.amount}")
        
        # Check All Payments by User
        print(f"\n💳 ALL PAYMENTS BY USER:")
        all_payments = Payment.objects.filter(payer=user)
        print(f"Total Payments: {all_payments.count()}")
        
        for payment in all_payments:
            print(f"   Payment {payment.transaction_id}:")
            print(f"     Status: {payment.status}")
            print(f"     Amount: PKR{payment.amount}")
            print(f"     Method: {payment.payment_method}")
            print(f"     Order: {payment.order.id if payment.order else 'None'}")
            print(f"     Job: {payment.job.id if payment.job else 'None'}")
            print(f"     Created: {payment.created_at}")
        
        # Check Jobs
        print(f"\n💼 JOBS:")
        jobs = user.posted_jobs.all()
        print(f"Total Jobs: {jobs.count()}")
        
        for job in jobs:
            print(f"   Job #{job.id}: {job.title}")
            print(f"     Status: {job.status}")
            print(f"     Budget: PKR{job.budget}")
            
        # Check if there are any payments in the system
        print(f"\n🔍 SYSTEM-WIDE PAYMENT CHECK:")
        all_system_payments = Payment.objects.all()
        print(f"Total Payments in System: {all_system_payments.count()}")
        
        if all_system_payments.count() > 0:
            print("Recent payments in system:")
            for payment in all_system_payments.order_by('-created_at')[:5]:
                print(f"   {payment.transaction_id}: {payment.payer.username} - PKR{payment.amount} - {payment.status}")
        
        # Calculate what dashboard should show
        print(f"\n📊 DASHBOARD CALCULATION:")
        
        completed_payments = Payment.objects.filter(payer=user, status='completed')
        total_spent = sum(p.amount for p in completed_payments)
        pending_payments = Payment.objects.filter(payer=user, status='pending').count()
        
        print(f"Completed Payments: {completed_payments.count()}")
        print(f"Total Spent: PKR{total_spent}")
        print(f"Pending Payments: {pending_payments}")
        print(f"Total Orders: {orders.count()}")
        print(f"Posted Jobs: {jobs.count()}")
        
    except CustomUser.DoesNotExist:
        print("❌ User 'shoaib' not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_other_users_with_data():
    """Check other users who have payments"""
    
    print(f"\n👥 USERS WITH PAYMENTS:")
    
    users_with_payments = CustomUser.objects.filter(
        buyer_payments__isnull=False
    ).distinct()
    
    for user in users_with_payments:
        payment_count = user.buyer_payments.count()
        completed_payments = user.buyer_payments.filter(status='completed').count()
        total_spent = sum(p.amount for p in user.buyer_payments.filter(status='completed'))
        
        print(f"   {user.username}: {payment_count} payments, {completed_payments} completed, PKR{total_spent} spent")

if __name__ == "__main__":
    print("🔍 Debugging User Data for Dashboard Stats")
    print("=" * 60)
    
    debug_shoaib_data()
    check_other_users_with_data()
    
    print("\n" + "=" * 60)
    print("✅ Debug completed!")