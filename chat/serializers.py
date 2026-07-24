from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Inbox, Message


User = get_user_model()


class InboxSerializer(serializers.ModelSerializer):
    chat_user = serializers.SerializerMethodField(read_only=True, method_name="get_chat_user")

    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "match",  "chat_user", "blocked", "blocked_by", )

    def get_chat_user(self, obj):
        data = {}
        match = obj.match
        request = self.context.get("request")
        users = {
            "sender": match.sender,
            "receiver": match.receiver
        }
        request_user_id = request.user.id
        chat_user = users['receiver'] if request_user_id == users['sender'].id else users['sender']
        data['name'] = chat_user.full_name
        data['photo'] = chat_user.get_photo()
        data['user_id'] = chat_user.id
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get("request")
        user = request.user
        response['last_message'] = None
        response['unseen_count'] = 0
        messages = Message.objects.filter(inbox=instance)

        if messages.exists():
            last_message = messages.last()
            unseen_messages = Message.objects.filter(inbox=instance, receiver=user, seen=False)
            response['unseen_count'] = unseen_messages.count()
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

    def validate(self, attrs):
        inbox = attrs['inbox']
        if inbox.blocked:
            raise serializers.ValidationError({"message": "Blocked Inbox"})
        return attrs

    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        sender_data = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        receiver_data = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        context['sender'] = sender_data
        context['receiver'] = receiver_data
        context['inbox_id'] = str(instance.inbox.inbox_id)
        context['last_message'] = {
            "sender": instance.sender.full_name,
            "receiver": instance.receiver.full_name,
            "message": instance.text,
            "seen": instance.seen,
            "timestamp": str(instance.timestamp)
        }
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
