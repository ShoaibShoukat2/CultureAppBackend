from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from .two_factor_utils import verify_totp_code, use_backup_code


class Setup2FASerializer(serializers.Serializer):
    """Serializer for 2FA setup"""
    pass


class Enable2FASerializer(serializers.Serializer):
    """Serializer for enabling 2FA"""
    totp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_totp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("TOTP code must be 6 digits")
        return valuea


class Disable2FASerializer(serializers.Serializer):
    """Serializer for disabling 2FA"""
    password = serializers.CharField(write_only=True)
    totp_code = serializers.CharField(max_length=6, min_length=6, required=False)
    backup_code = serializers.CharField(max_length=8, required=False)
    
    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('password')
        totp_code = attrs.get('totp_code')
        backup_code = attrs.get('backup_code')
        
        # Verify password first
        if not password:
            raise serializers.ValidationError({
                "password": ["Password is required to disable 2FA"]
            })
        
        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": ["Invalid password"]
            })
        
        # If user has 2FA enabled, require 2FA verification
        if user.two_factor_enabled:
            if not totp_code and not backup_code:
                raise serializers.ValidationError({
                    "totp_code": ["Please provide TOTP code from your authenticator app"],
                    "backup_code": ["Or provide a backup code instead"],
                    "message": "To disable 2FA, you need: 1) Your password AND 2) TOTP code from authenticator app OR backup code"
                })
            
            if totp_code:
                from .two_factor_utils import verify_totp_code
                if not verify_totp_code(user.two_factor_secret, totp_code):
                    raise serializers.ValidationError({
                        "totp_code": ["Invalid TOTP code. Check your authenticator app."]
                    })
            elif backup_code:
                from .two_factor_utils import use_backup_code
                if not use_backup_code(user, backup_code):
                    raise serializers.ValidationError({
                        "backup_code": ["Invalid or already used backup code"]
                    })
        
        return attrs


class LoginWith2FASerializer(serializers.Serializer):
    """Serializer for login with 2FA"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        return attrs


class Verify2FASerializer(serializers.Serializer):
    """Serializer for 2FA verification"""
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