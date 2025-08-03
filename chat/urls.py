from django.urls import path

from . import template_views

from .views import (
    ListInbox,
    ChatMessages
)

# Api
urlpatterns = [
    path("inbox/", ListInbox.as_view(), name='list-inbox'),
    path("messages/<uuid:inbox_id>/", ChatMessages.as_view(), name='chat-messages'),
]

# Templates views
urlpatterns += [
    path("<uuid:inbox_id>/", template_views.Chat.as_view(), name='chat'),
]