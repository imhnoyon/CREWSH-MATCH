from django.db import models
from django.conf import settings

from core.models import Ship
from core.models import Timestamp


class Plan(Timestamp):
    DURATION = (
        ("WEEKLY", "WEEKLY"),
        ("MONTHLY", "MONTHLY"),
        ("YEARLY", "YEARLY")
    )
    ship = models.ForeignKey(Ship, related_name='plans', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price_id = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=25, choices=list(DURATION))
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.name}"


class Subscription(Timestamp):
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='subscription', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    subscription_id = models.CharField(max_length=150)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user} subscribed to {self.plan}"



class PrivateMode(Timestamp):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='private_subscription', on_delete=models.CASCADE)
    payment_intent_id = models.CharField(max_length=150)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.full_name


