from django.dispatch import receiver
from django.db.models.signals import post_save

from chat.models import Inbox
from .models import Match, Notification


@receiver(post_save, sender=Match)
def signals_on_match_creation(instance, created, *args, **kwargs):
    if created:
        Inbox.objects.create(match=instance)
        users = (instance.sender, instance.receiver)
        notifications = [ Notification(user=user, match=instance) for user in users]
        Notification.objects.bulk_create(notifications)
