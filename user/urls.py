from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CreateUser,
    AuthToken,
    SendOtp,
    VerifyOtp,
    ChangePassword,
    ConfirmPasswordReset,
    UpdateUser,
    RetrieveProfile,
    UpdateProfile,
    UploadPhotos
)


app_name = "user"


urlpatterns = [
    path("create/", CreateUser.as_view(), name='register'),
    path("token/", AuthToken.as_view(), name='token'),
    path("token/refresh/", TokenRefreshView.as_view(), name='refresh-token'),
    path("verify/", VerifyOtp.as_view(), name='verify'),
    path("send-otp/", SendOtp.as_view(), name='send-otp'),
    path("change-password/", ChangePassword.as_view(), name='change-password'),
    path("confirm-password-reset/", ConfirmPasswordReset.as_view(), name='confirm-password-reset'),
    path("update/<int:pk>/", UpdateUser.as_view(), name='update-user'),
    path("retrieve-profile/<int:pk>/", RetrieveProfile.as_view(), name='retrieve-profile'),
    path("update-profile/<int:pk>/", UpdateProfile.as_view(), name='update-profile'),
    path("upload-photos/", UploadPhotos.as_view(), name='upload-photos'),
]

