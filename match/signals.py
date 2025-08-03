from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Match
from chat.models import Inbox


@receiver(post_save, sender=Match)
def create_inbox_on_new_match(instance, created, *args, **kwargs):
    if created:
        Inbox.objects.create(match=instance)
