from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import User

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    """
    Custom login API. Expects POST request with fields 'email' and 'password'.
    Only non-customer users are allowed to login.
    Returns auth token, user id, and email upon successful authentication.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
          
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Disallow login for customers as they require no authentication.
            if user.user_type == 'CUSTOMER':
                return Response(
                    {"error": "Customers do not require authentication."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "auth_token": token.key,
                "user_id": user.id,
                "email": user.email,
                "user_type": user.user_type
            })
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('user_type')

        # Validate required fields
        if not all([email, password, user_type]):
            return Response(
                {"error": "Email, password, and user_type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate user_type
        if user_type not in ['ADMIN', 'KITCHEN']:
            return Response(
                {"error": "Invalid user_type. Must be either 'ADMIN' or 'KITCHEN'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new user
        user = User.objects.create_user(
            email=email,
            password=password,
            user_type=user_type
        )

        # Create auth token
        token = Token.objects.create(user=user)

        return Response({
            "message": "User registered successfully",
            "auth_token": token.key,
            "user_id": user.id,
            "email": user.email,
            "user_type": user.user_type
        }, status=status.HTTP_201_CREATED)