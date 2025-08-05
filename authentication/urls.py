from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    Signup,
    Signin,
    ForgotPassword,
    ResendVerificationCode,
    VerifyEmail,
    VerifyResetCode,
    ChangePassword,
    ResetPassword,
)


app_name = "auth"


urlpatterns = [
    path("sign-up/", Signup.as_view(), name='register'),
    path("resend-verification-code/", ResendVerificationCode.as_view(), name='resend-verification-code'),
    path("verify-email/", VerifyEmail.as_view(), name='verify-email'),
    path("sign-in/", Signin.as_view(), name='signin'),
    path("forgot-password/", ForgotPassword.as_view(), name='forgot-password'),
    path("verify-reset-code/", VerifyResetCode.as_view(), name='verify-reset-password'),
    path("refresh/", TokenRefreshView.as_view(), name='refresh-token'),
    path("change-password/", ChangePassword.as_view(), name='change-password'),
    path("reset-password/", ResetPassword.as_view(), name='confirm-password-reset'),
]
