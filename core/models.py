from django.db import models
from django.conf import settings


class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Announcement(Timestamp):
    title = models.CharField(max_length=100)
    link = models.URLField()
    banner = models.ImageField(upload_to="announcement_banners")

    def __str__(self):
        return self.title


class Company(Timestamp):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return  self.name


class Ship(Timestamp):
    company = models.ForeignKey(Company, related_name='ships', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class PrivateModeSubscription(Timestamp):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='private_mode', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=4, decimal_places=2)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.user





