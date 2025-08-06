from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from user.models import Profile
from user.serializers import ProfileSerializer

from subscription.models import PrivateMode, Subscription
from subscription.serializers import (
    PrivateModeSerializer, SubscriptionSerializer
)

from .serializers import (
    AdminUserSerializer
)


class ListUser(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        return get_user_model().objects.order_by("-id").exclude(id=self.request.user.id)


class RetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = AdminUserSerializer
    queryset = get_user_model().objects.all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        full_name = self.request.data.get("full_name")
        email_address = self.request.data.get("email_address")

        serializer = ProfileSerializer(data=self.request.data)

        profile = Profile.objects.filter(user=user)

        if email_address and user.email_address != email_address:
            if get_user_model().objects.filter(email_address=email_address).exclude(id=user.id).exists():
                return Response({"message": "User with the email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            user.email_address = email_address

        if full_name and user.full_name != full_name:
            user.full_name = full_name

        if profile.exists():
            serializer = ProfileSerializer(instance=profile.first(), data=self.request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        user.save()
        user_serializer = AdminUserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class ListPrivateMode(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = PrivateModeSerializer
    queryset = PrivateMode.objects.order_by("-id")


class ListSubscription(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.order_by("-id")
