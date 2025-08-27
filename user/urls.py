from django.urls import path

from .views import (
    UpdateUser,
    RetrieveProfile,
    UpdateProfile,
    UploadPhotos,
    UpdatePhotos,
    UploadProfilePhoto,
    ViewUserDetails,
    Delete
)


app_name = "user"


urlpatterns = [
    path("update/<int:pk>/", UpdateUser.as_view(), name='update-user'),
    path("retrieve-profile/", RetrieveProfile.as_view(), name='retrieve-profile'),
    path("update-profile/", UpdateProfile.as_view(), name='update-profile'),
    path("upload-photos/", UploadPhotos.as_view(), name='upload-photos'),
    path("update-photos/", UpdatePhotos.as_view(), name='update-photos'),
    path("upload-profile-photo/", UploadProfilePhoto.as_view(), name='upload-profile-photo'),
    path("view-user-details/<int:pk>/", ViewUserDetails.as_view(), name='view-user-details'),
    path("delete/", Delete.as_view(), name='delete'),
]
