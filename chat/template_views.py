from django.db.models import Q
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from match.models import Match
from .models import Inbox, Message


class InboxList(LoginRequiredMixin, generic.ListView):
    login_url = "/admin/login/"
    model = Inbox
    template_name = "inbox.html"
    context_object_name = "inboxes"

    def get_queryset(self):
        friend_list = Match.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).filter(unfriended=False, blocked=False) \
        .values_list("id", flat=True)
        inboxes = Inbox.objects.filter(match__in=friend_list)
        return inboxes
    

class Chat(LoginRequiredMixin, generic.DetailView):
    login_url = "/admin/login/"
    model = Inbox
    template_name = "chat.html"
    context_object_name = "inbox"
    slug_url_kwarg = "inbox_id"
    slug_field = "inbox_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inbox = self.get_object()
        match_object = Match.objects.get(id=inbox.match.id)
        context['messages'] = Message.objects.filter(inbox=inbox)
        context['chating_to'] = match_object.sender if self.request.user.pk != match_object.sender.pk else match_object.receiver
        return context
