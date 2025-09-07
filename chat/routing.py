from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<str:inbox_id>/", consumers.ChatConsumer.as_asgi(), name='ws-chat-inbox'),
    path("ws/inbox/<int:user_id>/", consumers.InboxConsumer.as_asgi(), name='we-inbox-list'),
]