import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.models import Timestamp, Company, Ship

from .managers import  UserManager


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


class Otp(Timestamp):
    user = models.OneToOneField(User, related_name='otp', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name} - {self.code}"


class Profile(Timestamp):
    GENDER = (("MALE", "MALE"), ("FEMALE", "FEMALE"))
    GENDER_CHOICES = GENDER + (("BOTH", "BOTH"),)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(null=True)
    dob = models.DateField()
    gender = models.CharField(choices=list(GENDER), max_length=6)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    ship = models.ForeignKey(Ship, null=True, on_delete=models.SET_NULL)
    country = models.CharField()
    gender_preference = models.CharField(choices=list(GENDER_CHOICES), max_length=6)
    age_from = models.IntegerField()
    age_to = models.IntegerField()
    banned_countries = models.JSONField(default=list)

    def __str__(self):
        return self.user.name


class Image(models.Model):
    user = models.ForeignKey(User, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user_images")

    def __str__(self):
        return  f"{self.user.name} - {self.image.url}"


class Friend(models.Model):
    connection_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    unfriended = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ("sender", "receiver")
        )
        ordering = ['-id']

    def __str__(self):
        return f"{self.sender.name} sent a freind request to {self.receiver.name}"

