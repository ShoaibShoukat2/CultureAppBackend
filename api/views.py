# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .models import *


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Signup successful',
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SigninView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            return Response({
                'message': 'Login successful',
                'token': user_data['token'],
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'email': user_data['email']
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)






class ArtistProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve current user's artist profile"""
        try:
            profile = request.user.artist_profile
        except ArtistProfile.DoesNotExist:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ArtistProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        """Create artist profile"""
        if hasattr(request.user, 'artist_profile'):
            return Response({'detail': 'Artist profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ArtistProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update existing artist profile"""
        try:
            profile = request.user.artist_profile
        except ArtistProfile.DoesNotExist:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ArtistProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




