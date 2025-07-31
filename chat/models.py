import uuid
import pytz

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from user.models import Friend


class Inbox(models.Model):
    """
    Every Friend object will have an Inbox where two persons will chat
    We will show these inboxes at the user end
    When a user will click on an inbox, we will load all the messages belonging to that inbox
    This is important to handle things like
    Suppose, two persons befriend, chat in inbox.
    Now one unfriends another, then we must keep their inbox/messages.
    So we will set unfriended = True in Friend model, but we will be able to load all inboxes for the user
    as friend_obj is here that holds sender and receiver so we can just get inboxes
    friend_list = Friend.objects.filer(Q(sender=user) | Q(receiver=user)).filter(accepted=True, unfriended=False, blocked=False).value_list("id", flat=True)
    inboxes = Inbox.objects.filter(friend_id__in=friend_list)
    """
    inbox_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    friend_object = models.OneToOneField(Friend, related_name='inbox', on_delete=models.CASCADE)
    online_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return str(self.inbox_id)


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ('Text', 'Text'),
        ('Photo', 'Photo'),
        ('File', 'File'),
    )
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    seen = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content_object)

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


class BlockedInbox(models.Model):
    inbox = models.OneToOneField(Inbox, related_name='blocked_inboxes', on_delete=models.CASCADE)
    blocked_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='total_blocks', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='being_blocked', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.blocked_by.name} blocked this inbox"


class DeletedConversation(models.Model):
    inbox = models.ForeignKey(Inbox, related_name='deleted', on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='deleted_conversation', on_delete=models.CASCADE)
    deleted_at = models.DateTimeField()

    def __str__(self):
        return f"{self.deleted_by.name} deleted conversation at {self.deleted_at}"
