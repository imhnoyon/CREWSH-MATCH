from django.contrib import admin
from django.urls import path, include


api_urlpatterns = [
    path("auth/", include("user.urls")),
    path("chat/", include("chat.urls")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(api_urlpatterns))
]
