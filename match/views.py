from datetime import timedelta, date

from django.utils import timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import permissions

from rest_framework.response import Response

from user.models import Profile

from .models import Request, Match, Notification, Unliked

from .permissions import IsRequestReceiver
from .serializers import (
    RequestSerializer, MatchSerializer,
    MatchProfileSerializer, NotificationSerializer,
    UnlikeSerializer
)


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

        return Response(serializer.data, status=status.HTTP_200_OK)


class Unlike(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        unliked_user = get_object_or_404(get_user_model(), id=user_id)
        unlike, _ = Unliked.objects.get_or_create(by=self.request.user, user=unliked_user)
        serializer = UnlikeSerializer(unlike)
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


class ListMatchedProfile(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = MatchProfileSerializer

    def get_queryset(self):
        response = []
        profile = self.request.user.get_profile()
        two_days_ago = timezone.now() - timedelta(days=2)
        recent_unliked = Unliked.objects.filter(last_timestamp__gte=two_days_ago, by=self.request.user).values_list("user", flat=True)
        sent_requests = Request.objects.filter(sender=self.request.user).values_list("receiver")
        received_requests = Request.objects.filter(receiver=self.request.user).values_list("sender")

        if profile:
            gender_preference = profile.gender_preference
            age_from = profile.age_from
            age_to = profile.age_to
            today = date.today()
            # youngest acceptable
            max_dob = today.replace(year=today.year - age_from)
            # oldest acceptable
            min_dob = today.replace(year=today.year - age_to - 1) + timedelta(days=1)
            banned_countries = profile.banned_countries
            country = profile.country
            company = profile.company
            ship = profile.ship

            profile_queryset = Profile.objects.filter(
                dob__range=(min_dob, max_dob),
                ship=ship,
                company=company
            )

            if gender_preference != "Both":
                profile_queryset = profile_queryset.filter(
                    gender=gender_preference
                )

            matched_profile = profile_queryset.exclude(
                country__in=banned_countries
            ).exclude(
                user=self.request.user
            ).exclude(
                user__id__in=recent_unliked
            ).exclude(
                user__in=sent_requests
            ).exclude(
                user__is_superuser=True
            )

            return matched_profile

        return response


class ListNotification(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = NotificationSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
