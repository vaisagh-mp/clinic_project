from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status, permissions
from .serializers import UserSerializer, LoginSerializer, RegisterUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserAPIView(generics.CreateAPIView):
    """
    API endpoint to register users (Superadmin, Clinic, Doctor)
    and send welcome + password reset email.
    """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Generate password reset link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://3.110.189.17/reset-password/{uid}/{token}/"

        # Send welcome + reset email
        subject = "Welcome to Our Platform 🎉"
        message = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Welcome to our platform! We're excited to have you on board.\n\n"
            f"Please set your password using the link below:\n\n"
            f"{reset_link}\n\n"
            f"If you didn’t request this, please ignore this email.\n\n"
            f"Best regards,\nThe Team"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        return Response({
            "message": "User registered successfully. A welcome email has been sent.",
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


# -------------------------------
# Forgot Password API
# -------------------------------
class ForgotPasswordAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Create reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Frontend reset password link
        frontend_domain = "3.110.189.17"  # replace with production domain in deployment
        reset_link = f"{frontend_domain}/reset-password/{uid}/{token}/"

        # Send email
        send_mail(
            "Reset your password",
            f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email.",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent to your email."}, status=200)


# -------------------------------
# Reset Password Confirm API
# -------------------------------
class ResetPasswordConfirmAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user or token."}, status=400)

        # Verify token validity
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=400)

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not password or not confirm_password:
            return Response({"error": "Both password fields are required."}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        user.set_password(password)
        user.save()

        return Response({"message": "Password reset successful!"}, status=200)