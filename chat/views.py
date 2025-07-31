from django.db.models import Q
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from user.models import Friend
from .models import Inbox, Message

from user.mixins import ChatAccessRequired



class InboxList(LoginRequiredMixin, generic.ListView):
    login_url = "/admin/login/"
    model = Inbox
    template_name = "inbox.html"
    context_object_name = "inboxes"

    def get_queryset(self):
        friend_list = Friend.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).filter(accepted=True, unfriended=False, blocked=False) \
        .values_list("id", flat=True)
        inboxes = Inbox.objects.filter(friend_object__in=friend_list)
        return inboxes
    

class Chat(ChatAccessRequired, generic.DetailView):
    login_url = reverse_lazy("login")
    model = Inbox
    template_name = "chat.html"
    context_object_name = "inbox"
    slug_url_kwarg = "inbox_id"
    slug_field = "inbox_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inbox = self.get_object()
        friend_object = Friend.objects.get(id=inbox.friend_object.id)
        context['messages'] = Message.objects.filter(inbox=inbox)
        context['chating_to'] = friend_object.sender if self.request.user.pk != friend_object.sender.pk else friend_object.receiver
        return context
