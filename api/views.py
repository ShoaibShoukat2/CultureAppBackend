# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, SigninSerializer
from django.contrib.auth import login
from rest_framework.permissions import AllowAny

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = SignupSerializer(user)  # serialize the created user
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class SigninView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)  # Optional: only if using session login
            return Response({'message': 'Login successful', 'username': user.username})
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
