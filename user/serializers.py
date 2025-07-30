from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .utils import generate_otp

from .models import Otp, Profile, Image

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    profile = serializers.SerializerMethodField(method_name="get_profile")

    class Meta:
        model = User
        fields = (
            "id", "name", "email", "password", "password2", "photo",
            "is_active", "is_subscribed", "is_private", "is_banned",
            "created_at", "profile",
        )

    def validate_password2(self, value):
        password = self.initial_data.get("password")

        if password and value and password != value:
            raise serializers.ValidationError("Passwords mismatched.")
        
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create(
            is_active=False,
            **validated_data
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        self.validated_data.pop("password2", None)
        password = self.validated_data.pop("password", None)

        for attr, value in self.validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        response = super().get_token(user)
        return response
    
    # Override validate to return extra data in payload
    def validate(self, attrs):
        data = super().validate(attrs)
        return data
    

class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        email = attrs.get("email")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No user exists with the provided email address"})

        try:
            otp = user.otp
        except Otp.DoesNotExist:
            raise serializers.ValidationError({"code": "Please resume registration process"})

        return attrs
    
    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        otp = Otp.objects.get(user=user)
        otp.code = generate_otp()
        otp.created_at = timezone.now()
        otp.updated_at = timezone.now()
        otp.used = False
        otp.save()

        send_mail(
            subject="Account Verification",
            message=otp.code,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        return self.validated_data


class OptSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                raise serializers.ValidationError({"user": "User is already verified"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No user exists with the provided email address"})
        
        try:
            otp = user.otp
            self.otp = otp
        except Otp.DoesNotExist:
            raise serializers.ValidationError({"code": "No such otp found"})
        
        now = timezone.now()
        expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 60 * 15)
        expiry_time = otp.created_at + timedelta(seconds=expiry_seconds)

        if now > expiry_time:
            raise serializers.ValidationError({"code": "Otp expired. Try again"})

        if otp.code != code:
            raise serializers.ValidationError({"code": "Invalid otp"})

        if otp.used:
            raise serializers.ValidationError({"code": "Otp already used"})

        return attrs
    
    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        user.is_active = True
        user.save()

        self.otp.used = True
        self.otp.save()

        self.validated_data['user_id'] = user.id

        return {"success": True, **self.validated_data}
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        request = self.context['request']
        user = request.user

        if not user.check_password(value):
            raise serializers.ValidationError("Wrong password")

        return value
    
    def validate_confirm_password(self, value):
        new_password = self.initial_data.get("new_password")

        if new_password and value and new_password != value:
            raise serializers.ValidationError("Passwords mismatched")
        
        return value
    
    def save(self, **kwargs):
        request = self.context['request']
        user = request.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    otp = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_confirm_password(self, value):
        new_password = self.initial_data.get("new_password")

        if new_password and value and new_password != value:
            raise serializers.ValidationError("Passwords mismatched")

        return  value

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user registered with the provided user_id")

    def validate_otp(self, value):
        user_id = self.initial_data.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
            otp = Otp.objects.get(user=user, code=value)

        except (User.DoesNotExist, Otp.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid User Otp.")

        return value

    def validate(self, data):
        try:
            self.user = User.objects.get(pk=data['user_id'])
            self.otp = Otp.objects.get(user=self.user, code=data['otp'])

        except (User.DoesNotExist, Otp.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid Otp.")

        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        self.otp.used = True
        self.otp.save()
        return self.user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "user", "image", )


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image", )


class MultipleImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=False)

    def validate_images(self, value):
        size_in_mb = 2
        max_size = size_in_mb * 1024 * 1024
        for image in value:
            if image.size > max_size:
                raise serializers.ValidationError(f"File must not exceed {size_in_mb} Mb")
        return value

    def create(self, validated_data):
        images = self.validated_data['images']
        request = self.context.get("request")

        image_objects = [ Image(user=request.user, image=image) for image in images]
        return Image.objects.bulk_create(image_objects)
