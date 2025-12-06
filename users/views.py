from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from drf_spectacular.utils import extend_schema



# Create your views here.


class RegisterAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'messege':'Register Successful'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginSerializer},
    )
    def post(self, request):
        identifier = request.data.get("username")   # username OR email from frontend
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("LOGIN ATTEMPT:", identifier, password)

        # Find user by username OR email
        user = User.objects.filter(
            Q(username=identifier) | Q(email=identifier)
        ).first()

        if not user:
            print("USER NOT FOUND")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check password manually
        if not user.check_password(password):
            print("PASSWORD MISMATCH FOR USER:", user.username)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: block / active checks
        if user.blocked:
            return Response(
                {"message": "Your account has been blocked"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.is_active:
            return Response(
                {"message": "Account is not active"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_admin = getattr(user, "role", None) == "admin"

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print("🔥 LOGIN ENDPOINT USED. USER ROLE:", user.role)

        response = Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.username,
                    "role": user.role,
                    "is_admin": is_admin,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )

        # Set cookies for SimpleJWT
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response

    
class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            })

    
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]   

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        return response

