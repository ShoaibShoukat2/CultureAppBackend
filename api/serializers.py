# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *
from rest_framework.authtoken.models import Token


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
        # Create token for the new user
        Token.objects.create(user=user)
        return user



class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "No user found with this email."})
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})
        if not user.is_active:
            raise serializers.ValidationError({"account": "User account is disabled."})

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }





class ArtistProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtistProfile
        fields = [
            'id',
            'username',
            'bio',
            'skills',
            'experience_level',
            'hourly_rate',
            'portfolio_description',
            'rating',
            'total_projects_completed',
            'total_earnings',
            'is_available',
            'completion_rate',
        ]
        read_only_fields = ['rating', 'total_projects_completed', 'total_earnings', 'completion_rate']

    def get_completion_rate(self, obj):
        return obj.calculate_completion_rate()





