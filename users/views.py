
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User


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

    def post(self, request):
        identifier = request.data.get("username")   
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"error": "Username and password required"}, status=400)

        print("LOGIN ATTEMPT:", identifier, password)

        
        user_obj = (
            User.objects.filter(username=identifier).first()
            or User.objects.filter(email=identifier).first()
        )

        if user_obj:
           
            user = authenticate(username=user_obj.username, password=password)
        else:
            user = None

        print("AUTH RESULT:", user)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        # ---- your token logic (unchanged) ----
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.username
            },
            "access_token": access_token,
            "refresh_token": refresh_token
        }, status=200)


        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,        
            samesite="Lax",
        )

       
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
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
            'id': user.id,
            'username': user.username,
            'email': user.email
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

