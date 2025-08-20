from typing import Any
from tokenize import TokenError
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .utils import generate_otp

from user.models import (
    AccountVerificationOtp, Profile, PasswordResetOtp
)

User = get_user_model()

EMAIL_SUBJECTS = {
    "account_verification": "Verify Account for Crew Match",
    "rest_password": "Reset Password for Crew Match"
}


class BaseOtpSerializer(serializers.Serializer):
    def save(self, user, instance, **kwargs):
        model_instance = instance

        if isinstance(model_instance, PasswordResetOtp):
            model_instance.user = user

        model_instance.code = generate_otp()
        model_instance.created_at = timezone.now()
        model_instance.updated_at = timezone.now()
        model_instance.used = False
        model_instance.save()

        return model_instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "user_id", "full_name", "email_address", "password", "password2", "photo",
            "is_active", "is_subscribed", "is_private", "is_banned",
            "created_at",
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
        response['is_trial_active'] = user.is_trial_active
        return response

    # Override validate to return extra data in payload
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token

        exp_timestamp = access_token['exp']  # seconds
        exp_millis = int(exp_timestamp * 1000)

        return {
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "access_token_valid_till": exp_millis,
            "user_id": str(self.user.id),
            "role": self.user.role,
            "profile": self.user.has_profile(),
        }


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    default_error_messages = {
        "no_active_account": _("No active account found for the given token.")
    }

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        try:
            refresh = self.token_class(attrs["refresh_token"])
        except TokenError:
            raise ValidationError({
                "message": "Your session has expired. Please log in again.",
                "error": "invalid_token"
            })
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id and (
                user := get_user_model().objects.get(
                    **{api_settings.USER_ID_FIELD: user_id}
                )
        ):
            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        data = {"access_token": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()

            data["refresh_token"] = str(refresh)

        return data


class ForgotPasswordSerializer(BaseOtpSerializer):
    email_address = serializers.EmailField()

    def validate(self, attrs):
        email_address = attrs.get("email_address")

        try:
            user = User.objects.get(email_address=email_address)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user exists with the provided email address"})

        return attrs

    def save(self, **kwargs):
        user = User.objects.get(email_address=self.validated_data['email_address'])
        instance = PasswordResetOtp()
        verification = super().save(user=user, instance=instance, **kwargs)

        expires_at = verification.created_at + timedelta(minutes=30)
        expires_at_millis = int(expires_at.timestamp() * 1000)

        send_mail(
            subject=EMAIL_SUBJECTS['rest_password'],
            message=verification.code,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email_address],
            fail_silently=True
        )
        response = {
            "user_id": user.id,
            "expires_at": expires_at_millis
        }
        return response


class VerifyResetCodeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    verification_code = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        verification_code = attrs.get("verification_code")

        try:
            self.user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user exists with the provided user id"})

        code = PasswordResetOtp.objects.filter(user=self.user, code=verification_code)

        if not code.exists():
            raise serializers.ValidationError({"message": "Invalid verification code"})

        self.otp = code.first()

        now = timezone.now()

        if now > self.otp.expired_at:
            raise serializers.ValidationError({"message": "Otp expired. Try again"})

        if self.otp.code != verification_code:
            raise serializers.ValidationError({"message": "Invalid otp"})

        if self.otp.used:
            raise serializers.ValidationError({"message": "Otp already used"})

        return attrs

    def save(self, **kwargs):

        response = {
            "secret_key": self.otp.secret_key
        }
        return response


class ResendVerificationCodeSerializer(BaseOtpSerializer):
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        user_id = attrs.get("user_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user exists with the provided user id"})

        try:
            otp = user.otp
        except AccountVerificationOtp.DoesNotExist:
            raise serializers.ValidationError({"message": "Please resume registration process"})

        return attrs

    def save(self, **kwargs):
        user = User.objects.get(id=self.validated_data['user_id'])
        instance = AccountVerificationOtp.objects.get(user=user)
        otp = super().save(user=user, instance=instance, **kwargs)

        send_mail(
            subject="Account Verification",
            message=otp.code,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email_address],
            fail_silently=True
        )
        return self.validated_data


class VerifyOptSerializerWithUserId(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            user = User.objects.get(id=user_id)
            if user.is_active:
                raise serializers.ValidationError({"message": "User is already verified"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user exists with the provided email address"})

        try:
            otp = user.otp
            self.otp = otp
        except AccountVerificationOtp.DoesNotExist:
            raise serializers.ValidationError({"message": "No such otp found"})

        now = timezone.now()
        expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 60 * 15)
        expiry_time = otp.created_at + timedelta(seconds=expiry_seconds)

        if now > expiry_time:
            raise serializers.ValidationError({"message": "Otp expired. Try again"})

        if otp.code != code:
            raise serializers.ValidationError({"message": "Invalid otp"})

        if otp.used:
            raise serializers.ValidationError({"message": "Otp already used"})

        return attrs

    def save(self, **kwargs):
        user = User.objects.get(id=self.validated_data['user_id'])
        user.is_active = True
        user.save()

        self.otp.used = True
        self.otp.save()

        profile = Profile.objects.filter(user=user)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        exp_timestamp = access_token['exp']  # seconds since epoch
        exp_millis = int(exp_timestamp * 1000)
        response = {
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "access_token_valid_till": exp_millis,
            "user_id": user.id,
            "role": user.role,
            "profile": profile.exists()
        }
        return response


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_confirm_password(self, value):
        new_password = self.initial_data.get("new_password")

        if new_password and value and new_password != value:
            raise serializers.ValidationError("Passwords mismatched")

        return value

    def validate(self, attrs):
        old_password = attrs['old_password']
        request = self.context['request']
        user = request.user

        if not user.check_password(old_password):
            raise serializers.ValidationError({"message": "Wrong password"})

        return attrs

    def save(self, **kwargs):
        request = self.context['request']
        user = request.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    secret_key = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)
    # confirm_password = serializers.CharField(write_only=True)

    # def validate_confirm_password(self, value):
    #     new_password = self.initial_data.get("new_password")
    #
    #     if new_password and value and new_password != value:
    #         raise serializers.ValidationError("Passwords mismatched")
    #
    #     return  value

    def validate(self, data):
        user_id = data.get("user_id")
        secret_key = data.get("secret_key")

        try:
            User.objects.get(id=user_id)

        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user registered with the provided user_id"})

        try:
            self.user = User.objects.get(pk=user_id)
            self.otp = PasswordResetOtp.objects.get(user=self.user, secret_key=secret_key)

            if self.otp.used:
                raise serializers.ValidationError({"message": "Secret key already used"})

        except (User.DoesNotExist, PasswordResetOtp.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError({"message": "Invalid verification code."})

        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        self.otp.used = True
        self.otp.save()
        return self.user
