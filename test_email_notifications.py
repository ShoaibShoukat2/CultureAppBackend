#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.models import Order, Payment, CustomUser
from api.email_service import EmailService
from decimal import Decimal
import uuid

def test_payment_confirmation_email():
    """Test payment confirmation email with new content"""
    print("🧪 Testing Payment Confirmation Email...")
    
    try:
        # Get a user
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found")
            return
        
        # Create a test payment
        payment = Payment.objects.create(
            payer=user,
            amount=Decimal('150.00'),
            payment_method='stripe',
            status='completed',
            transaction_id=f'test_{uuid.uuid4().hex[:8]}'
        )
        
        print(f"✅ Test payment created: {payment.transaction_id}")
        
        # Test email service
        result = EmailService.send_payment_confirmation(payment)
        
        if result:
            print("✅ Payment confirmation email sent successfully!")
            print(f"📧 Email sent to: {user.email}")
        else:
            print("❌ Failed to send payment confirmation email")
            
        # Clean up
        payment.delete()
        
    except Exception as e:
        print(f"❌ Error testing payment email: {str(e)}")

def test_order_confirmation_email():
    """Test order confirmation email with new content"""
    print("\n🧪 Testing Order Confirmation Email...")
    
    try:
        # Get latest order
        order = Order.objects.order_by('-created_at').first()
        if not order:
            print("❌ No orders found")
            return
            
        print(f"✅ Testing with Order #{order.id}")
        
        # Test email service
        result = EmailService.send_purchase_confirmation(order)
        
        if result:
            print("✅ Order confirmation email sent successfully!")
            print(f"📧 Email sent to: {order.buyer.email}")
        else:
            print("❌ Failed to send order confirmation email")
            
    except Exception as e:
        print(f"❌ Error testing order email: {str(e)}")

def test_email_settings():
    """Test email configuration"""
    print("\n⚙️ Testing Email Configuration...")
    
    try:
        from django.core.mail import send_mail
        
        # Get a user email
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found for email test")
            return
            
        print(f"📧 Testing email to: {user.email}")
        
        # Send test email
        result = send_mail(
            subject='🧪 Test Email - CultureUp',
            message='This is a test email to verify the new "Purchased Successfully" content is working!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        if result:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")

def check_email_templates():
    """Check if email templates exist and are readable"""
    print("\n📄 Checking Email Templates...")
    
    import os
    from django.template.loader import get_template
    
    templates = [
        'emails/purchase_confirmation.html',
        'emails/purchase_confirmation.txt'
    ]
    
    for template_name in templates:
        try:
            template = get_template(template_name)
            print(f"✅ Template found: {template_name}")
        except Exception as e:
            print(f"❌ Template error {template_name}: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Email Notifications with 'Purchased Successfully' Content")
    print("=" * 70)
    
    # Check email templates
    check_email_templates()
    
    # Test email configuration
    test_email_settings()
    
    # Test payment confirmation
    test_payment_confirmation_email()
    
    # Test order confirmation
    test_order_confirmation_email()
    
    print("\n" + "=" * 70)
    print("✅ Email testing completed!")