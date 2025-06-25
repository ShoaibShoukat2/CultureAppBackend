# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'user_type', 'phone_number', 'profile_image']
        read_only_fields = ['id']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'buyer'),
            phone_number=validated_data.get('phone_number'),
            profile_image=validated_data.get('profile_image')
        )
        return user









class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Try to find the user by email
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "No user found with this email."})

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError({"account": "User account is disabled."})

        return user
    




