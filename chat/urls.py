from django.urls import path

from . import template_views

from .views import (
    ListInbox,
    ChatMessages,
    Block,
    UnBlock
)

# Api
urlpatterns = [
    path("inbox/", ListInbox.as_view(), name='list-inbox'),
    path("block/<int:pk>/", Block.as_view(), name='block'),
    path("unblock/<int:pk>/", UnBlock.as_view(), name='unblock'),
    path("messages/<uuid:inbox_id>/", ChatMessages.as_view(), name='chat-messages'),
]

# Templates views
urlpatterns += [
    path("<uuid:inbox_id>/", template_views.Chat.as_view(), name='chat'),
]
