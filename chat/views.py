from django.db.models import Max, F, DateTimeField, Case, When, Q

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from match.models import Match
from .models import Inbox, Message, BlockedInbox

from .permissions import HasInboxAccess, IsBlocker
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
        match_list = Match.objects.filter(Q(sender=user) | Q(receiver=user)).filter(unfriended=False).values_list("id",
                                                                                                                  flat=True)
        # Annotate with the last message timestamp (if any)
        inboxes = Inbox.objects.filter(match__id__in=match_list).annotate(
            last_msg_time=Max('message__timestamp'),
            sort_time=Case(
                When(last_msg_time__isnull=False, then=F('last_msg_time')),
                default=F('created_at'),
                output_field=DateTimeField()
            )
        ).order_by('sort_time')

        return inboxes


class ChatMessages(generics.RetrieveAPIView):
    permission_classes = [HasInboxAccess, ]
    serializer_class = ChatMessageSerializer
    queryset = Inbox.objects.all()
    lookup_url_kwarg = "inbox_id"
    lookup_field = "inbox_id"

    def retrieve(self, request, *args, **kwargs):
        unread_messages = Message.objects.filter(inbox=self.get_object(), receiver=self.request.user, seen=False)
        unread_messages.update(seen=True)
        return super().retrieve(request, *args, **kwargs)


class Block(generics.UpdateAPIView):
    permission_classes = [HasInboxAccess, ]
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()

    def update(self, request, *args, **kwargs):
        inbox = self.get_object()
        match = inbox.match
        blocked_by = self.request.user
        blocked_user = match.receiver if blocked_by.id == match.sender.id else match.sender

        inbox.blocked = True
        inbox.blocked_by = blocked_by
        match.blocked = True
        inbox.save()
        match.save()

        BlockedInbox.objects.create(
            inbox=inbox,
            blocked_by=blocked_by,
            blocked_user=blocked_user
        )
        serializer = self.get_serializer(inbox)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnBlock(generics.UpdateAPIView):
    permission_classes = [HasInboxAccess, IsBlocker, ]
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()

    def update(self, request, *args, **kwargs):
        inbox = self.get_object()
        match = inbox.match
        inbox.blocked = False
        inbox.blocked_by = None
        match.blocked = False
        inbox.save()
        match.save()
        BlockedInbox.objects.filter(inbox=inbox).delete()
        serializer = self.get_serializer(inbox)
        return Response(serializer.data, status=status.HTTP_200_OK)
