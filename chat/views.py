from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions


from .models import Inbox
from match.models import Match
from .permissions import HasInboxAccess
from .serializers import (
    InboxSerializer,
    ChatMessageSerializer,
)


class ListInbox(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()

    def get_queryset(self):
        user = self.request.user
        match_list = Match.objects.filter(Q(sender=user) | Q(receiver=user)).filter(
            unfriended=False, blocked=False).values_list(
            "id", flat=True
        )
        inboxes = Inbox.objects.filter(match__id__in=match_list)
        return inboxes


class ChatMessages(generics.RetrieveAPIView):
    permission_classes = [HasInboxAccess, ]
    serializer_class = ChatMessageSerializer
    queryset = Inbox.objects.all()
    lookup_url_kwarg = "inbox_id"
    lookup_field = "inbox_id"


