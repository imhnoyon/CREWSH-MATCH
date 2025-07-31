from django.urls import path

from . import apis
from . import views

# Api
urlpatterns = [
    path("send-message/<uuid:inbox_id>/", apis.SendMessage.as_view(), name='send-message'),
    path("send-multiple-photo/<uuid:inbox_id>/", apis.SendMultiplePhoto.as_view(), name='send-multiple-photo'),
]

# Templates views
urlpatterns += [
    path("<uuid:inbox_id>/", views.Chat.as_view(), name='chat'),
]