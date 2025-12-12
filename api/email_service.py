from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for handling email notifications"""
    
    @staticmethod
    def send_purchase_confirmation(order):
        """
        Send purchase confirmation email to buyer
        """
        try:
            # Prepare context data
            context = {
                'buyer_name': order.buyer.get_full_name() or order.buyer.username,
                'order_id': order.id,
                'order_date': order.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'order_status': order.get_status_display(),
                'order_type': order.get_order_type_display(),
                'total_amount': order.total_amount,
                'shipping_address': order.shipping_address,
                'artwork_items': order.artwork_items.all(),
                'equipment_items': order.equipment_items.all(),
            }
            
            # Render email templates
            html_message = render_to_string('emails/purchase_confirmation.html', context)
            text_message = render_to_string('emails/purchase_confirmation.txt', context)
            
            # Create email
            subject = f'Order Confirmation #{order.id} - CultureUp'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [order.buyer.email]
            
            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_message, "text/html")
            
            result = email.send()
            
            if result:
                logger.info(f"Purchase confirmation email sent successfully for order #{order.id}")
                return True
            else:
                logger.error(f"Failed to send purchase confirmation email for order #{order.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending purchase confirmation email for order #{order.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_confirmation(payment):
        """
        Send payment confirmation email
        """
        try:
            # Determine recipient and context based on payment type
            if payment.order:
                # Order payment
                recipient = payment.payer
                context = {
                    'user_name': recipient.get_full_name() or recipient.username,
                    'payment_id': payment.transaction_id,
                    'amount': payment.amount,
                    'payment_method': payment.get_payment_method_display(),
                    'payment_date': payment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    'order_id': payment.order.id if payment.order else None,
                    'job_title': payment.job.title if payment.job else None,
                    'payment_type': 'Order Payment' if payment.order else 'Job Payment'
                }
            elif payment.job:
                # Job payment - notify both payer and payee
                EmailService._send_job_payment_notification(payment)
                return True
            else:
                logger.warning(f"Payment {payment.transaction_id} has no associated order or job")
                return False
            
            # Create simple payment confirmation email
            subject = f'Payment Confirmation - ${payment.amount} - CultureUp'
            message = f"""
Hello {context['user_name']},

Your payment has been processed successfully!

Payment Details:
- Payment ID: {context['payment_id']}
- Amount: ${context['amount']}
- Payment Method: {context['payment_method']}
- Date: {context['payment_date']}
- Type: {context['payment_type']}
{f"- Order ID: #{context['order_id']}" if context['order_id'] else ""}
{f"- Job: {context['job_title']}" if context['job_title'] else ""}

Thank you for using CultureUp!

Best regards,
CultureUp Team
            """
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False
            )
            
            if result:
                logger.info(f"Payment confirmation email sent for payment {payment.transaction_id}")
                return True
            else:
                logger.error(f"Failed to send payment confirmation email for payment {payment.transaction_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending payment confirmation email for payment {payment.transaction_id}: {str(e)}")
            return False
    
    @staticmethod
    def _send_job_payment_notification(payment):
        """
        Send job payment notifications to both buyer and artist
        """
        try:
            # Notify buyer (payer)
            buyer_subject = f'Payment Sent - ${payment.amount} - CultureUp'
            buyer_message = f"""
Hello {payment.payer.get_full_name() or payment.payer.username},

Your payment has been sent successfully!

Payment Details:
- Payment ID: {payment.transaction_id}
- Amount: ${payment.amount}
- Payment Method: {payment.get_payment_method_display()}
- Job: {payment.job.title}
- Artist: {payment.payee.get_full_name() or payment.payee.username}
- Date: {payment.created_at.strftime('%B %d, %Y at %I:%M %p')}

The payment is currently held in escrow and will be released to the artist upon job completion.

Thank you for using CultureUp!

Best regards,
CultureUp Team
            """
            
            send_mail(
                subject=buyer_subject,
                message=buyer_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payment.payer.email],
                fail_silently=False
            )
            
            # Notify artist (payee)
            if payment.payee:
                artist_subject = f'Payment Received - ${payment.amount} - CultureUp'
                artist_message = f"""
Hello {payment.payee.get_full_name() or payment.payee.username},

Great news! You've received a payment for your work.

Payment Details:
- Payment ID: {payment.transaction_id}
- Amount: ${payment.amount}
- Job: {payment.job.title}
- Client: {payment.payer.get_full_name() or payment.payer.username}
- Date: {payment.created_at.strftime('%B %d, %Y at %I:%M %p')}

The payment is currently held in escrow and will be released to you upon job completion.

Keep up the great work!

Best regards,
CultureUp Team
                """
                
                send_mail(
                    subject=artist_subject,
                    message=artist_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[payment.payee.email],
                    fail_silently=False
                )
            
            logger.info(f"Job payment notifications sent for payment {payment.transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending job payment notifications for payment {payment.transaction_id}: {str(e)}")
            return False
    
    @staticmethod
    def send_order_status_update(order, old_status, new_status):
        """
        Send email when order status changes
        """
        try:
            status_messages = {
                'confirmed': 'Your order has been confirmed and is being processed.',
                'shipped': 'Great news! Your order has been shipped and is on its way.',
                'delivered': 'Your order has been delivered successfully!',
                'cancelled': 'Your order has been cancelled. If you have any questions, please contact support.'
            }
            
            subject = f'Order #{order.id} Status Update - {new_status.title()} - CultureUp'
            message = f"""
Hello {order.buyer.get_full_name() or order.buyer.username},

Your order status has been updated.

Order Details:
- Order ID: #{order.id}
- Previous Status: {old_status.title()}
- New Status: {new_status.title()}
- Total Amount: ${order.total_amount}

{status_messages.get(new_status, 'Your order status has been updated.')}

You can track your order status in your account dashboard.

Thank you for choosing CultureUp!

Best regards,
CultureUp Team
            """
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.buyer.email],
                fail_silently=False
            )
            
            if result:
                logger.info(f"Order status update email sent for order #{order.id}")
                return True
            else:
                logger.error(f"Failed to send order status update email for order #{order.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending order status update email for order #{order.id}: {str(e)}")
            return False