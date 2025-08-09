from django.db.models import Sum
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.models import Company, Ship, Announcement, Settings
from core.serializers import (
    CompanySerializer, ShipSerializer, AnnouncementSerializer, SettingsSerializer
)

from user.models import Profile
from user.serializers import ProfileSerializer

from match.models import Match

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


class RetrieveUpdateDeleteUser(generics.RetrieveUpdateDestroyAPIView):
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


class ListCreateCompany(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class RetrieveDeleteCompany(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class ListCreateShip(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = ShipSerializer
    queryset = Ship.objects.all()


class RetrieveUpdateDeleteShip(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = ShipSerializer
    queryset = Ship.objects.all()


class CreateAnnounceMent(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    parser_classes = [MultiPartParser, FormParser, ]
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()

    def create(self, request, *args, **kwargs):
        Announcement.objects.all().delete()
        return super().create(request, *args, **kwargs)


class UpdateAccount(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = AdminUserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser, ]

    def post(self, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteSettings(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = SettingsSerializer

    def get_object(self):
        return Settings.objects.first()

    def get(self, *args, **kwargs):
        instance = self.get_object()
        serializer = SettingsSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        instance = self.get_object()
        serializer = SettingsSerializer(instance, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class Dashboard(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def get(self, *args, **kwargs):
        users = get_user_model().objects.all()
        matches = Match.objects.all()
        subscriptions = Subscription.objects.all()
        private_modes = PrivateMode.objects.all()
        subscription_earning = subscriptions.aggregate(Sum("amount_paid"))
        private_mode_earning = private_modes.aggregate(Sum("amount_paid"))
        sb_earn = subscription_earning['amount_paid__sum'] if subscription_earning['amount_paid__sum'] else 0
        prm_earn = private_mode_earning['amount_paid__sum'] if private_mode_earning['amount_paid__sum'] else 0
        profiles = Profile.objects.all()
        profile_count = profiles.count()
        males = profiles.filter(gender="MALE")
        females = profiles.filter(gender="FEMALE")
        print(("males", males.count()))
        print(("females", females.count()))

        data = {
            "user_count": users.count(),
            "match_count": matches.count(),
            "subscription_count": subscriptions.count(),
            "total_earning": sb_earn + prm_earn,
            "user_list": AdminUserSerializer(users.exclude(id=self.request.user.id), many=True).data,
            "gender_data": {
                "male_percentage": (males.count() / profile_count) * 100,
                "female_percentage": (females.count()/ profile_count) * 100
            }
        }

        return Response(data, status=status.HTTP_200_OK)

