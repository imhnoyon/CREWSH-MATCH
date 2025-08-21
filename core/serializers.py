from rest_framework import serializers

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
        return response


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ("id", "title", "link", "banner", )


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ("terms_and_conditions", )


class CompanyAndShipSerializer(CompanySerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['ships'] = ShipSerializer(instance.ships.all(), many=True).data
        return response

