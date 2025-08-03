from rest_framework import serializers

from .models import Inbox, Message



class InboxSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField(read_only=True, method_name="get_name")

    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "match",  "name", )

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
        fields = ['id', 'sender', 'receiver', "text", "seen", "deleted", "timestamp"]

    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        return context

class ChatMessageSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField(read_only=True, method_name="get_messages")

    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "messages", )

    def get_messages(self, obj):
        messages = obj.message_set.all()
        return  MessageSerializer(messages, many=True).data
