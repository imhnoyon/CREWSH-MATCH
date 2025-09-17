import uuid
from datetime import date

from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.models import Timestamp, Company, Ship

from .managers import  UserManager


class OtpCode(models.Model):
    code = models.CharField(max_length=6)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, Timestamp):
    full_name = models.CharField(max_length=150)
    email_address = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    photo = models.ImageField(null=True, blank=True, upload_to="user_images")
    objects = UserManager()

    USERNAME_FIELD = "email_address"
    REQUIRED_FIELDS = ["full_name", ]
    
    class Meta:
        ordering = ["-id"]

    @property
    def role(self):
        role = "user"
        if self.is_superuser:
            role = "admin"
        return role

    def __str__(self):
        return self.full_name

    def get_photo(self):
        photo = ""
        if self.photo:
            photo = f"{settings.DOMAIN}{self.photo.url}"
        return photo

    def get_profile(self):
        try:
            return self.profile
        except Exception as e:
            return False

    def has_profile(self) -> bool:
        return True if self.get_profile() else False

    @property
    def is_trial_active(self):
        return timezone.now() <= self.created_at + timedelta(days=45)


class AccountVerificationOtp(OtpCode):
    user = models.OneToOneField(User, related_name='otp', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.full_name} - {self.code}"

    def save(self, *args, **kwargs):
        if not self.used:
            expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 60 * 15)
            self.expired_at = timezone.now() + timedelta(seconds=expiry_seconds)
        return super().save(*args, **kwargs)


class PasswordResetOtp(OtpCode):
    user = models.ForeignKey(User, related_name='verification_codes', on_delete=models.CASCADE)
    secret_key = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.user.full_name} - {self.code}"

    def save(self, *args, **kwargs):
        expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 60 * 15)
        self.expired_at = timezone.now() + timedelta(seconds=expiry_seconds)
        return super().save(*args, **kwargs)


class Profile(Timestamp):
    GENDER = (("Men", "Men"), ("Women", "Women"))
    GENDER_CHOICES = GENDER + (("Both", "Both"),)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(null=True)
    dob = models.DateField()
    gender = models.CharField(choices=list(GENDER), max_length=6)
    company = models.ForeignKey(Company, related_name='company_profiles', on_delete=models.CASCADE)
    ship = models.ForeignKey(Ship, related_name='ship_profiles', on_delete=models.CASCADE)
    country = models.CharField()
    gender_preference = models.CharField(choices=list(GENDER_CHOICES), max_length=6)
    age_from = models.IntegerField()
    age_to = models.IntegerField()
    banned_countries = models.JSONField(default=list)

    def __str__(self):
        return self.user.full_name

    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))


class Image(models.Model):
    user = models.ForeignKey(User, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user_images")

    def __str__(self):
        return  f"{self.user.full_name} - {self.image.url}"

    def get_url(self):
        return settings.DOMAIN + self.image.url





