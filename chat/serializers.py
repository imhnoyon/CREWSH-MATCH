from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Inbox, Message


User = get_user_model()


class InboxSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField(read_only=True, method_name="get_name")

    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "match",  "name", "blocked", )

    def get_name(self, obj):
        match = obj.match
        request = self.context.get("request")
        users = {
            "sender": match.sender,
            "receiver": match.receiver
        }
        request_user_id = request.user.id
        name = users['receiver'].full_name if request_user_id == users['sender'].id else users['sender'].full_name
        return name

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['last_message'] = None
        messages = Message.objects.filter(inbox=instance)

        if messages.exists():
            last_message = messages.last()
            response['last_message'] = {
                "sender": last_message.sender.full_name,
                "receiver": last_message.receiver.full_name,
                "message": last_message.text,
                "seen": last_message.seen,
                "timestamp": last_message.timestamp
            }

        return response


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', "inbox", 'sender', 'receiver', "text", "seen", "deleted", "timestamp"]
        extra_kwargs = {
            "inbox": {"write_only": True}
        }

    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        sender_data = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        receiver_data = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        context['sender'] = sender_data
        context['receiver'] = receiver_data
        return context

    def save(self, **kwargs):
        receiver = self.validated_data['receiver']
        inbox = self.validated_data['inbox']

        if receiver in inbox.online_users.all():
            self.validated_data['seen'] = True

        super().save(**kwargs)

class ChatMessageSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField(read_only=True, method_name="get_messages")

    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "messages", )

    def get_messages(self, obj):
        messages = obj.message_set.all()
        return  MessageSerializer(messages, many=True).data
