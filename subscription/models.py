from django.db import models
from django.conf import settings

from core.models import Timestamp


class Plan(Timestamp):
    name = models.CharField(max_length=150)
    price_id = models.CharField(max_length=150)
    duration_text = models.CharField(max_length=250, help_text="1 Week, 1 Month, 1 Year")
    display_price = models.CharField(max_length=250, help_text="9.99/month, 333.99/yearly")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.display_price}"


class Subscription(Timestamp):
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='subscription', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    subscription_id = models.CharField(max_length=150)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} subscribed to {self.plan}"
