from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from .serializers import UserSerializer, LoginSerializer, RegisterUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserAPIView(generics.CreateAPIView):
    """
    API endpoint to register users (Superadmin, Clinic, Doctor)
    """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]  # anyone can register initially

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User registered successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    

class RoleBasedLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # First check username/password manually
        login_serializer = LoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)
        user = login_serializer.validated_data["user"]

        # Get JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
            "redirect_to": self.get_redirect(user),
        }, status=status.HTTP_200_OK)

    def get_redirect(self, user):
        if user.is_superuser or user.role == "ADMIN":
            return "admin_panel:dashboard"
        elif user.role == "CLINIC":
            return "clinic_panel:dashboard"
        elif user.role == "DOCTOR":
            return "doctor_panel:dashboard"
        return None


class LogoutAPIView(TokenObtainPairView):
    """
    Blacklist the refresh token to logout user.
    """
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
