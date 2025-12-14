import secrets
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import PaymentVerificationSession, Payment
from .two_factor_utils import verify_totp_code, use_backup_code


# Configuration
MIN_2FA_AMOUNT = Decimal('5000.00')  # PKR 5000
MAX_VERIFICATION_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 30
SESSION_DURATION_MINUTES = 15


def payment_requires_2fa(payment):
    """Check if payment requires 2FA verification"""
    return (payment.payer.two_factor_enabled and 
            payment.amount >= MIN_2FA_AMOUNT)


def create_payment_verification_session(payment, verification_type='payment_confirm'):
    """Create a payment verification session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(minutes=SESSION_DURATION_MINUTES)
    
    # Clean up old sessions for this payment
    PaymentVerificationSession.objects.filter(
        payment=payment,
        expires_at__lt=timezone.now()
    ).delete()
    
    session = PaymentVerificationSession.objects.create(
        payment=payment,
        session_token=session_token,
        expires_at=expires_at,
        verification_type=verification_type
    )
    
    return session


def verify_payment_2fa_session(session_token):
    """Verify payment 2FA session token"""
    try:
        session = PaymentVerificationSession.objects.get(
            session_token=session_token,
            is_used=False
        )
        
        if session.is_expired():
            session.delete()
            return None, "Session expired"
            
        return session, None
    except PaymentVerificationSession.DoesNotExist:
        return None, "Invalid session"


def verify_payment_2fa_code(session, totp_code=None, backup_code=None):
    """Verify 2FA code for payment"""
    payment = session.payment
    user = payment.payer
    
    # Check if verification is locked
    if payment.is_verification_locked():
        return False, "Verification locked due to too many failed attempts"
    
    # Verify 2FA code
    verification_success = False
    
    if totp_code:
        verification_success = verify_totp_code(user.two_factor_secret, totp_code)
    elif backup_code:
        verification_success = use_backup_code(user, backup_code)
    
    if verification_success:
        # Mark payment as 2FA verified
        payment.is_2fa_verified = True
        payment.verification_attempts = 0
        payment.verification_locked_until = None
        payment.save()
        
        # Mark session as used
        session.is_used = True
        session.save()
        
        return True, "Verification successful"
    else:
        # Increment failed attempts
        payment.verification_attempts += 1
        
        # Lock if max attempts reached
        if payment.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
            payment.verification_locked_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            payment.save()
            return False, f"Too many failed attempts. Locked for {LOCKOUT_DURATION_MINUTES} minutes"
        
        payment.save()
        remaining_attempts = MAX_VERIFICATION_ATTEMPTS - payment.verification_attempts
        return False, f"Invalid code. {remaining_attempts} attempts remaining"


def reset_payment_verification(payment):
    """Reset payment verification status"""
    payment.is_2fa_verified = False
    payment.verification_attempts = 0
    payment.verification_locked_until = None
    payment.save()
    
    # Delete any existing sessions
    PaymentVerificationSession.objects.filter(payment=payment).delete()


def get_payment_verification_status(payment):
    """Get payment verification status"""
    return {
        'requires_2fa': payment_requires_2fa(payment),
        'is_verified': payment.is_2fa_verified,
        'is_locked': payment.is_verification_locked(),
        'attempts_remaining': MAX_VERIFICATION_ATTEMPTS - payment.verification_attempts,
        'lockout_expires': payment.verification_locked_until.isoformat() if payment.verification_locked_until else None
    }


def can_process_payment(payment):
    """Check if payment can be processed"""
    if not payment_requires_2fa(payment):
        return True, "No 2FA required"
    
    if payment.is_2fa_verified:
        return True, "2FA verified"
    
    if payment.is_verification_locked():
        return False, "Verification locked"
    
    return False, "2FA verification required"