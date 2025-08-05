from django.db.models import Q

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

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
            unfriended=False).values_list(
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


class Block(generics.UpdateAPIView):
    permission_classes = [HasInboxAccess, ]
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()

    def update(self, request, *args, **kwargs):
        inbox = self.get_object()
        match = inbox.match
        inbox.blocked = True
        match.blocked = True
        inbox.save()
        match.save()
        serializer = self.get_serializer(inbox)
        return Response(serializer.data, status=status.HTTP_200_OK)
