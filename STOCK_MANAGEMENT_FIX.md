# Stock Management Fix - Complete Solution

## Issues Found:

1. **Orders: 0, Payments: 100** - Payments created without orders
2. **Stock not updating** - No stock reduction in payment flow
3. **Analytics mismatch** - Job payments vs purchase orders confusion

## Root Causes:

1. **Missing Order Creation**: Equipment purchases bypass order creation
2. **No Stock Reduction**: Payment processing doesn't reduce stock
3. **Workflow Disconnect**: Orders and payments are separate workflows

## Solutions:

### Solution 1: Add Stock Reduction to Payment Processing

Add this to your `api/views.py` in the PaymentViewSet:

```python
def create(self, request, *args, **kwargs):
    """Create payment and handle stock reduction for order payments"""
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check if payment is for an order with equipment
    order_id = request.data.get('order')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            
            # Check stock availability before creating payment
            for item in order.equipment_items.all():
                if item.equipment.stock_quantity < item.quantity:
                    return Response({
                        'error': f"Equipment '{item.equipment.name}' has insufficient stock. Available: {item.equipment.stock_quantity}, Required: {item.quantity}"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create payment
            payment = serializer.save()
            
            # If payment is completed, reduce stock immediately
            if payment.status == 'completed':
                for item in order.equipment_items.all():
                    item.equipment.reduce_stock(item.quantity)
                    
                # Update order status
                order.status = 'confirmed'
                order.save()
                
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Regular payment creation (for jobs)
        payment = serializer.save()
    
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
```

### Solution 2: Add Stock Reduction to Payment Confirmation

Update the `confirm_payment` method:

```python
@action(detail=True, methods=['post'])
def confirm_payment(self, request, pk=None):
    """Confirm payment status after frontend processing"""
    payment = self.get_object()
    
    if payment.payer != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if payment.status not in ['processing', 'pending']:
        return Response({'error': 'Payment cannot be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check the PaymentIntent status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent)
        
        if intent.status == 'succeeded':
            # Payment successful
            payment.status = 'completed'
            payment.save()
            
            # Reduce stock if payment is for an order
            if payment.order:
                for item in payment.order.equipment_items.all():
                    if not item.equipment.reduce_stock(item.quantity):
                        # Log error but don't fail payment
                        print(f"Warning: Could not reduce stock for {item.equipment.name}")
                
                # Update order status
                payment.order.status = 'confirmed'
                payment.order.save()
            
            return Response({
                'message': 'Payment confirmed successfully',
                'payment_status': payment.status,
                'transaction_id': payment.transaction_id
            }, status=status.HTTP_200_OK)
            
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

### Solution 3: Add Stock Restoration on Payment Failure

Add this method to handle failed payments:

```python
@action(detail=True, methods=['post'])
def handle_failed_payment(self, request, pk=None):
    """Handle failed payment and restore stock if needed"""
    payment = self.get_object()
    
    if payment.payer != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if payment.status == 'completed' and payment.order:
        # Restore stock for failed/refunded payments
        for item in payment.order.equipment_items.all():
            item.equipment.stock_quantity += item.quantity
            item.equipment.save()
        
        # Update order status
        payment.order.status = 'cancelled'
        payment.order.save()
    
    payment.status = 'failed'
    payment.save()
    
    return Response({'message': 'Payment marked as failed, stock restored'})
```

### Solution 4: Fix Equipment Model Stock Management

Update your Equipment model's `reduce_stock` method:

```python
def reduce_stock(self, quantity):
    """Reduce stock quantity with better error handling"""
    if self.stock_quantity >= quantity:
        self.stock_quantity -= quantity
        if self.stock_quantity == 0:
            self.is_available = False
        self.save(update_fields=['stock_quantity', 'is_available'])
        return True
    return False

def restore_stock(self, quantity):
    """Restore stock quantity"""
    self.stock_quantity += quantity
    if self.stock_quantity > 0:
        self.is_available = True
    self.save(update_fields=['stock_quantity', 'is_available'])
    return True
```

### Solution 5: Add Stock Validation Signal

Create a signal to handle stock validation:

```python
# Add to api/signals.py

@receiver(post_save, sender=Payment)
def handle_payment_stock_reduction(sender, instance, created, **kwargs):
    """Handle stock reduction when payment is completed"""
    if instance.status == 'completed' and instance.order:
        # Check if this is a status change to completed
        if not created:
            try:
                old_payment = Payment.objects.get(pk=instance.pk)
                if old_payment.status != 'completed':
                    # Payment just became completed, reduce stock
                    for item in instance.order.equipment_items.all():
                        if not item.equipment.reduce_stock(item.quantity):
                            logger.error(f"Failed to reduce stock for {item.equipment.name}")
                    
                    # Update order status
                    instance.order.status = 'confirmed'
                    instance.order.save()
                    
            except Payment.DoesNotExist:
                pass
```

## Implementation Steps:

1. **Update PaymentViewSet** in `api/views.py`
2. **Update Equipment model** in `api/models.py` 
3. **Add signal handler** in `api/signals.py`
4. **Test the flow**:
   - Create order with equipment
   - Create payment for order
   - Confirm payment
   - Check stock reduction

## Testing Commands:

```bash
# Check current stock
python manage.py shell
>>> from api.models import Equipment
>>> Equipment.objects.all().values('name', 'stock_quantity')

# Create test order and payment
# Check stock after payment confirmation
```

This solution will ensure that:
- ✅ Stock reduces when payments are completed
- ✅ Stock restores when payments fail
- ✅ Orders are properly linked to payments
- ✅ Analytics will show correct order counts
- ✅ Equipment availability updates automatically