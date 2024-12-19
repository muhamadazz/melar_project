from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, ChangePasswordSerializer
from django.conf import settings

class RegisterView(APIView):
    """Handle user registration and return relevant feedback."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User registered successfully.",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Registration failed. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Login using JWT and return access and refresh tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({
                "message": "Login successful.",
                "tokens": response.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Login failed. Please check your credentials."
        }, status=response.status_code)


class LogoutView(APIView):
    """Handle user logout by blacklisting their refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({
                "message": "Refresh token is missing in the request."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Assumes simplejwt.blacklist is configured
            return Response({
                "message": "Logout successful. Token has been blacklisted."
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                "message": "Logout failed due to an invalid token.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's profile."""
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Update the user's profile with feedback messages."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Profile update failed. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """API untuk mengubah password pengguna."""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Menyimpan password baru setelah validasi berhasil
        serializer.save()
        
        return Response({"detail": "Password berhasil diubah."}, status=status.HTTP_200_OK)