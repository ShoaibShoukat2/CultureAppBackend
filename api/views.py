# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, SigninSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login

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




    


