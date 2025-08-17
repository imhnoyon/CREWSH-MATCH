from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "full_name", "email_address", "photo",
            "is_active", "is_subscribed", "is_private",
            "created_at",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['photo'] = instance.get_photo()
        profile = instance.get_profile()
        response['profile'] = profile
        if profile:
            response['profile'] = {"gender": profile.gender, "company": profile.company.name, "ship": profile.ship.name}
        return response
