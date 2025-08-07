from django.urls import path

from .views import (
    UpdateUser,
    RetrieveProfile,
    UpdateProfile,
    UploadPhotos,
    UpdatePhotos
)


app_name = "user"


urlpatterns = [
    path("update/<int:pk>/", UpdateUser.as_view(), name='update-user'),
    path("retrieve-profile/", RetrieveProfile.as_view(), name='retrieve-profile'),
    path("update-profile/", UpdateProfile.as_view(), name='update-profile'),
    path("upload-photos/", UploadPhotos.as_view(), name='upload-photos'),
    path("update-photos/", UpdatePhotos.as_view(), name='update-photos'),
]
