from rest_framework import serializers

from .models import Request, Match


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("sender", "receiver", )

    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        return context


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            "id",
            "connection_id",
            "sender",
            "receiver",
            "blocked",
            "unfriended",
            "sent_at",
            "updated_at",
        )


    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        return context