from django.urls import path
from .views import RoleBasedLoginView, LogoutAPIView, RegisterUserAPIView, ForgotPasswordAPIView, ResetPasswordConfirmAPIView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "accounts"

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='user-register'),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/<uidb64>/<token>/", ResetPasswordConfirmAPIView.as_view(), name="password-reset-confirm"),
]
