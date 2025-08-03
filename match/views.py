from django.db.models import Q

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from .models import Request, Match
from .permissions import IsRequestReceiver
from .serializers import RequestSerializer, MatchSerializer


class SendRequest(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = RequestSerializer
    queryset = Request.objects.all()


class AcceptRequest(generics.UpdateAPIView):
    permission_classes = [IsRequestReceiver, ]
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    lookup_url_kwarg = "request_id"
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        match, _ = Match.objects.get_or_create(sender=instance.sender, receiver=instance.receiver)

        instance.accepted = True
        instance.save()

        serializer = MatchSerializer(match)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListRequests(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = RequestSerializer
    queryset = Request.objects.all()

    def get_queryset(self):
        return Request.objects.filter(receiver=self.request.user, accepted=False)


class ListMatches(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = MatchSerializer
    queryset = Match.objects.all()

    def get_queryset(self):
        user = self.request.user
        match_list = Match.objects.filter(Q(sender=user) | Q(receiver=user)).filter(unfriended=False, blocked=False)
        return match_list
