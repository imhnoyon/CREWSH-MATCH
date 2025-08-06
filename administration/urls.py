from django.urls import path

from .views import (
    ListUser,
    RetrieveUpdateDelete,
    ListPrivateMode,
    ListSubscription
)


urlpatterns = [
    path("user/list/", ListUser.as_view(), name='list-user'),
    path("user/retrieve-update-delete/<int:pk>/", RetrieveUpdateDelete.as_view(), name='retrieve-update-delete'),
    path("subscription/private-mode/", ListPrivateMode.as_view(), name='list-private-mode'),
    path("subscription/list/", ListSubscription.as_view(), name='list-subscription')
]

