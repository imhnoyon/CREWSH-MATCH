from django.db.models import Q, Sum

from rest_framework import serializers

from match.models import Match
from user.models import Profile
from subscription.models import Subscription
from .models import Company, Ship, Announcement, Settings


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "created_at", )


class ShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ("id", "company", "name", "created_at", )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        company = instance.company
        response['company'] = {"id": company.id, "name": company.name}

        request = self.context.get("request")

        if request:
            user = request.user
            if user.is_staff and user.is_superuser:
                response['total_users'] = Profile.objects.filter(ship=instance).exclude(user__is_superuser=True).count()
                response['total_subscribers'] = Profile.objects.filter(user__is_subscribed=True,
                                                                       ship=instance).count()
                response['total_matches'] = Match.objects.filter(
                    Q(sender__profile__ship=instance) |
                    Q(receiver__profile__ship=instance)
                ).distinct().count()
                ship_earning = Subscription.objects.filter(user__profile__ship=instance).aggregate(Sum("amount_paid"))
                print(Subscription.objects.filter(user__profile__ship=instance))
                # print(ship_earning)
                response['total_earning'] = ship_earning['amount_paid__sum'] if ship_earning['amount_paid__sum'] else 0

        return response


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ("id", "title", "link", "banner", "ship", )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        ship = instance.ship
        response['ship'] = {"name": ship.name}
        return response


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ("terms_and_conditions", )


class CompanyAndShipSerializer(CompanySerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['ships'] = ShipSerializer(instance.ships.all(), many=True).data
        return response

