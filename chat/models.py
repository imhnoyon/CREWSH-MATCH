import uuid
import pytz

from django.db import models
from django.conf import settings

from match.models import Match


class Inbox(models.Model):
    """
    Every Match object will have an Inbox where two persons will chat
    We will show these inboxes at the user end
    When a user will click on an inbox, we will load all the messages belonging to that inbox
    This is important to handle things like
    Suppose, two persons befriend, chat in inbox.
    Now one unfriends another, then we must keep their inbox/messages.
    So we will set unfriended = True in Match model, but we will be able to load all inboxes for the user
    as match_object is here that holds sender and receiver so we can just get inboxes
    match_list = Match.objects.filter(Q(sender=user) | Q(receiver=user)).filter(unfriended=False).value_list("id", flat=True)
    inboxes = Inbox.objects.filter(match_object_id__in=match_list)
    """
    inbox_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    match = models.OneToOneField(Match, related_name='inbox', on_delete=models.CASCADE)
    online_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return str(self.inbox_id)


class Message(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    seen = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.text)
    
    @property
    def sent_at(self):
        dhaka_tz = pytz.timezone("Asia/Dhaka")
        local_time = self.timestamp.astimezone(dhaka_tz)
        return local_time.strftime("%H:%M")
    
    @property
    def extension(self):
        ext = ""

        if self.message_type == "File":
             name = self.content_object.file.url
             ext = name.split(".").pop()

        return ext
    
