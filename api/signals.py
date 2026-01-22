from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, Payment, ArtworkOrderItem, EquipmentOrderItem
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    """
    Send confirmation email when a new order is created
    """
    if created:
        try:
            # Calculate total amount if not already calculated
            if instance.total_amount == 0:
                instance.calculate_total()
            
            # Send purchase confirmation email
            EmailService.send_purchase_confirmation(instance)
            logger.info(f"Order confirmation email triggered for order #{instance.id}")
            
        except Exception as e:
            logger.error(f"Error in order confirmation email signal for order #{instance.id}: {str(e)}")

@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Track order status changes to send update emails
    """
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # Store old status for post_save signal
                instance._old_status = old_order.status
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def send_order_status_update_email(sender, instance, created, **kwargs):
    """
    Send email when order status is updated
    """
    if not created and hasattr(instance, '_old_status'):
        try:
            EmailService.send_order_status_update(
                instance, 
                instance._old_status, 
                instance.status
            )
            logger.info(f"Order status update email sent for order #{instance.id}")
            
        except Exception as e:
            logger.error(f"Error in order status update email signal for order #{instance.id}: {str(e)}")

@receiver(post_save, sender=Payment)
def send_payment_confirmation_email(sender, instance, created, **kwargs):
    """
    Send confirmation email when a payment is completed and handle stock reduction
    """
    if created or (instance.status == 'completed' and not hasattr(instance, '_email_sent')):
        try:
            EmailService.send_payment_confirmation(instance)
            # Mark email as sent to avoid duplicate emails
            instance._email_sent = True
            logger.info(f"Payment confirmation email triggered for payment {instance.transaction_id}")
            
        except Exception as e:
            logger.error(f"Error in payment confirmation email signal for payment {instance.transaction_id}: {str(e)}")

@receiver(post_save, sender=Payment)
def handle_payment_stock_reduction(sender, instance, created, **kwargs):
    """Handle stock reduction when payment status changes to completed"""
    if not created and instance.status == 'completed' and instance.order:
        try:
            # Get the previous state to check if status just changed
            if hasattr(instance, '_old_status') and instance._old_status != 'completed':
                # Payment just became completed, reduce stock
                for item in instance.order.equipment_items.all():
                    if not item.equipment.reduce_stock(item.quantity):
                        logger.error(f"Failed to reduce stock for {item.equipment.name}")
                
                # Update order status
                instance.order.status = 'confirmed'
                instance.order.save()
                logger.info(f"Stock reduced for payment {instance.transaction_id}")
                
        except Exception as e:
            logger.error(f"Error in stock reduction for payment {instance.transaction_id}: {str(e)}")

@receiver(pre_save, sender=Payment)
def track_payment_status_change(sender, instance, **kwargs):
    """Track payment status changes"""
    if instance.pk:  # Only for existing payments
        try:
            old_payment = Payment.objects.get(pk=instance.pk)
            instance._old_status = old_payment.status
        except Payment.DoesNotExist:
            pass

@receiver(post_save, sender=ArtworkOrderItem)
def notify_artist_of_artwork_sale(sender, instance, created, **kwargs):
    """
    Notify artist when their artwork is purchased
    """
    if created:
        try:
            artist = instance.artwork.artist
            buyer = instance.order.buyer
            
            subject = f'Your Artwork "{instance.artwork.title}" Has Been Sold! - CultureUp'
            message = f"""
Hello {artist.get_full_name() or artist.username},

Congratulations! Your artwork has been purchased.

Sale Details:
- Artwork: {instance.artwork.title}
- Buyer: {buyer.get_full_name() or buyer.username}
- Quantity: {instance.quantity}
- Price: PKR{instance.price} each
- Total: PKR{instance.get_total_price()}
- Order ID: #{instance.order.id}
- Sale Date: {instance.order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Your earnings from this sale will be processed according to our payment schedule.

Keep creating amazing art!

Best regards,
CultureUp Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[artist.email],
                fail_silently=False
            )
            
            logger.info(f"Artist notification email sent for artwork sale: {instance.artwork.title}")
            
        except Exception as e:
            logger.error(f"Error sending artist notification email for artwork sale: {str(e)}")

@receiver(post_save, sender=EquipmentOrderItem)
def send_equipment_purchase_notification(sender, instance, created, **kwargs):
    """
    Send notification for equipment purchases (to admin/store manager)
    """
    if created:
        try:
            # Notify store admin about equipment sale
            admin_emails = ['shoaibahmadbhatti6252@gmail.com']  # Add your admin emails
            
            subject = f'Equipment Sold: {instance.equipment.name} - CultureUp'
            message = f"""
Equipment Sale Notification:

Equipment: {instance.equipment.name}
Buyer: {instance.order.buyer.get_full_name() or instance.order.buyer.username}
Buyer Email: {instance.order.buyer.email}
Quantity: {instance.quantity}
Price: PKR{instance.price} each
Total: PKR{instance.get_total_price()}
Order ID: #{instance.order.id}
Sale Date: {instance.order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Shipping Address:
{instance.order.shipping_address}

Please process this order for shipment.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False
            )
            
            logger.info(f"Equipment sale notification sent for: {instance.equipment.name}")
            
        except Exception as e:
            logger.error(f"Error sending equipment sale notification: {str(e)}")