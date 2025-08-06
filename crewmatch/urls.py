from django.contrib import admin
from django.urls import path, include


api_urlpatterns = [
    path("auth/", include("authentication.urls")),
    path("user/", include("user.urls")),
    path("match/", include("match.urls")),
    path("chat/", include("chat.urls")),
    path("subscription/", include("subscription.urls")),
    path("payment/", include("payment.urls")),
    path("administration/", include("administration.urls")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(api_urlpatterns))
]
