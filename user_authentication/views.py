from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    """
    Custom login API. Expects POST request with fields 'email' and 'password'.
    Only non-customer users are allowed to login.
    Returns auth token, user id, first name, and email upon successful authentication.
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
                "first_name": user.first_name,
                "email": user.email,
            })
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )