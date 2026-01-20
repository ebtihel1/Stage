from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer
)
from .models import User


class RegisterView(generics.CreateAPIView):
    """Endpoint pour créer un compte"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Utilisateur créé avec succès",
                    "user": UserProfileSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint pour se connecter (obtenir JWT)"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    """Endpoint pour rafraîchir le token JWT"""
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint pour récupérer et mettre à jour le profil de l'utilisateur connecté"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profil mis à jour avec succès",
                    "user": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)