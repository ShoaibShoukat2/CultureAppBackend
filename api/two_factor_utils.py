import pyotp
import qrcode
import io
import base64
import secrets
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import TwoFactorSession


def generate_secret_key():
    """Generate a random secret key for TOTP"""
    return pyotp.random_base32()


def generate_qr_code(user, secret_key):
    """Generate QR code for 2FA setup"""
    # Create TOTP URI
    totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name=user.email,
        issuer_name="CultureUp"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{qr_code_base64}"


def verify_totp_code(secret_key, code):
    """Verify TOTP code"""
    totp = pyotp.TOTP(secret_key)
    return totp.verify(code, valid_window=1)  # Allow 30 seconds window


def generate_backup_codes(count=10):
    """Generate backup codes for 2FA"""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()  # 8-character hex code
        codes.append(code)
    return codes


def create_2fa_session(user):
    """Create a temporary 2FA session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
    
    # Clean up old sessions
    TwoFactorSession.objects.filter(
        user=user,
        expires_at__lt=timezone.now()
    ).delete()
    
    session = TwoFactorSession.objects.create(
        user=user,
        session_token=session_token,
        expires_at=expires_at
    )
    
    return session


def verify_2fa_session(session_token):
    """Verify 2FA session token"""
    try:
        session = TwoFactorSession.objects.get(
            session_token=session_token,
            is_used=False
        )
        
        if session.is_expired():
            session.delete()
            return None
            
        return session
    except TwoFactorSession.DoesNotExist:
        return None


def use_backup_code(user, code):
    """Use a backup code for 2FA"""
    if code.upper() in user.backup_codes:
        user.backup_codes.remove(code.upper())
        user.save()
        return True
    return False