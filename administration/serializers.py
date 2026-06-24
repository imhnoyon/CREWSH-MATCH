from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        response = super().get_token(user)
        return response

    # Override validate to return extra data in payload
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            print(self.user)
        except AuthenticationFailed:
            raise AuthenticationFailed(_("Invalid email or password. Please try again."))

        if not self.user.is_superuser:
            raise AuthenticationFailed(_("Invalid email or password. Please try again."))

        refresh = self.get_token(self.user)
        access_token = refresh.access_token

        exp_timestamp = access_token['exp']  # seconds
        exp_millis = int(exp_timestamp * 1000)

        return {
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "access_token_valid_till": exp_millis,
            "user_id": self.user.id,
            "role": self.user.role,
            "profile": self.user.has_profile(),
        }


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
        response['user_images'] = [ {"url": image.get_url()} for image in instance.images.all()]
        profile = instance.get_profile()
        response['profile'] = profile
        if profile:
            response['profile'] = {"gender": profile.gender, "company": profile.company.name, "ship": profile.ship.name}
        return response


from marketplace.models import Product
class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields =['id', 'title', 'description','image','created_at', 'user']
         
    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "email_address": obj.user.email_address,
            "photo": obj.user.get_photo(),
        }



class ServiceSerializer2(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields =['id', 'title', 'description','image','created_at', 'user']
    
    