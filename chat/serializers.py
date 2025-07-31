from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from .models import Inbox, Message
from content.models import Text, Photo, File
from content.serializers import (
    TextSerializer, PhotoSerializer, FileSerializer, DynamicContentSerializer
)

CONTENT_TYPE_MAP = {
    'text': (Text, TextSerializer),
    'photo': (Photo, PhotoSerializer),
    "file": (File, FileSerializer)
}


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ("id", "inbox_id", "friend_object"
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        sender = instance.friend_object.sender
        receiver = instance.friend_object.receiver
        response['sender'] = {"id": sender.id, "username": sender.username}
        response['receiver'] = {"id": receiver.id, "username": receiver.username}
        return response
    

class MessageSerializer(serializers.ModelSerializer):
    """Dynamic message serializer to create a message of different types such as Text, Photo, File"""
    content_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', "inbox", "message_type",
                  'content_object',"seen", "deleted", "timestamp"
                  ]

    def get_content_object(self, obj):
        if isinstance(obj.content_object, Text):
            return TextSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Photo):
            return PhotoSerializer(obj.content_object).data
        elif isinstance(obj.content_object, File):
            return FileSerializer(obj.content_object).data
        return None

    def create(self, validated_data):
        content_data = {
            "content_type_key": self.initial_data.get('content_type_key'),
            "content_data": self.initial_data.get("content_data")
        }
        content_serializer = DynamicContentSerializer(data=content_data)
        content_serializer.is_valid(raise_exception=True)
        content_obj = content_serializer.save()

        content_type_key = content_serializer.validated_data["content_type_key"]
        model_class = CONTENT_TYPE_MAP[content_type_key][0]
        content_type = ContentType.objects.get_for_model(model_class)
        
        return Message.objects.create(
            content_type=content_type,
            object_id=content_obj.id,
            **validated_data
        )
    

class BaseMultiplePhotoMessageSerializer(serializers.ModelSerializer):
    """Serializer to create messages when multiple photos are sent"""
    content_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', "inbox", "message_type",
                  'content_object', "object_id", "seen", "deleted", "timestamp"]

    def get_content_object(self, obj):
        if isinstance(obj.content_object, Text):
            return TextSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Photo):
            return PhotoSerializer(obj.content_object).data
        elif isinstance(obj.content_object, File):
            return FileSerializer(obj.content_object).data
        return None

    def create(self, validated_data):
        content_type = ContentType.objects.get_for_model(model=CONTENT_TYPE_MAP["photo"][0])
        return Message.objects.create(
            content_type=content_type,
            **validated_data
        )


class InboxMessageSerializer(InboxSerializer):
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        messages = MessageSerializer(Message.objects.filter(inbox=instance), many=True)
        response['messages'] = messages.data
        return response
