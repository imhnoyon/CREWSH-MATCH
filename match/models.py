import uuid
from django.db import models
from django.conf import settings

from core.models import Timestamp


class Request(Timestamp):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_request', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            ("sender", "receiver")
        )

    def __str__(self):
        return f"{self.sender.full_name} liked {self.receiver.full_name}"


class Match(models.Model):
    connection_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='accepted_matches', on_delete=models.CASCADE)
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
        return f"{self.sender.full_name} matched with {self.receiver.full_name}"

