from rest_framework import serializers
from .models import Payment, PaymentVerificationSession


class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for payment 2FA verification"""
    session_token = serializers.CharField()
    totp_code = serializers.CharField(max_length=6, min_length=6, required=False)
    backup_code = serializers.CharField(max_length=8, required=False)
    
    def validate(self, attrs):
        totp_code = attrs.get('totp_code')
        backup_code = attrs.get('backup_code')
        
        if not totp_code and not backup_code:
            raise serializers.ValidationError("Either TOTP code or backup code is required")
        
        if totp_code and not totp_code.isdigit():
            raise serializers.ValidationError("TOTP code must be 6 digits")
        
        return attrs


class PaymentStatusSerializer(serializers.ModelSerializer):
    """Serializer for payment status with 2FA info"""
    requires_2fa = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'amount', 'status', 
            'requires_2fa', 'is_2fa_verified', 'verification_status'
        ]
    
    def get_requires_2fa(self, obj):
        from .payment_2fa_utils import payment_requires_2fa
        return payment_requires_2fa(obj)
    
    def get_verification_status(self, obj):
        from .payment_2fa_utils import get_payment_verification_status
        return get_payment_verification_status(obj)


class InitiatePaymentSerializer(serializers.Serializer):
    """Serializer for initiating payment with 2FA check"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=[
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer')
    ])
    order_id = serializers.IntegerField(required=False)
    job_id = serializers.IntegerField(required=False)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value