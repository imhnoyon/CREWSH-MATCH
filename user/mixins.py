from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin

from .models import Friend
from chat.models import Inbox


class ChatAccessRequired(AccessMixin):
    login_url = reverse_lazy("login")
    message = "You are not authorized to view this content"

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect(self.login_url)
    #
    #     inbox = Inbox.objects.get(inbox_id=self.kwargs.get("inbox_id"))
    #     friendship = Friend.objects.get(id=inbox.friend_object.id)
    #
    #     users = (friendship.sender, friendship.receiver)
    #
    #     if not request.user in users:
    #         self.handle_no_permission()
    #
    #     return super().dispatch(request, *args, **kwargs)