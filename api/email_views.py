from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, Payment
from .email_service import EmailService
import json

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def test_email_connection(request):
    """Test basic email connection"""
    try:
        result = send_mail(
            subject='Test Email - CultureUp',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False
        )
        
        if result:
            return JsonResponse({
                'success': True,
                'message': f'Test email sent successfully to {request.user.email}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send test email'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Email test failed: {str(e)}'
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def send_order_email(request):
    """Manually send order confirmation email"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'message': 'Order ID is required'
            })
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Order not found'
            })
        
        result = EmailService.send_purchase_confirmation(order)
        
        if result:
            return JsonResponse({
                'success': True,
                'message': f'Order confirmation email sent successfully for order #{order_id}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send order confirmation email'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def send_payment_email(request):
    """Manually send payment confirmation email"""
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        if not payment_id:
            return JsonResponse({
                'success': False,
                'message': 'Payment ID is required'
            })
        
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Payment not found'
            })
        
        result = EmailService.send_payment_confirmation(payment)
        
        if result:
            return JsonResponse({
                'success': True,
                'message': f'Payment confirmation email sent successfully for payment {payment.transaction_id}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send payment confirmation email'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@staff_member_required
def email_settings_info(request):
    """Get current email settings information"""
    settings_info = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
    
    return JsonResponse({
        'success': True,
        'settings': settings_info
    })