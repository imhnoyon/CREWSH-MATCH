from rest_framework import serializers

from user.models import Profile
from .models import Request, Match, Notification, Unliked


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
        inbox = instance.inbox
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo()}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo()}
        context['inbox_id'] = inbox.inbox_id
        return context


class MatchProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id")
    full_name = serializers.CharField(source='user.full_name')
    company = serializers.CharField(source='company.name')
    ship = serializers.CharField(source='ship.name')

    class Meta:
        model = Profile
        fields = (
            "id",
            "user_id",
            "full_name",
            "bio",
            "dob",
            "gender",
            "company",
            "ship",
            "country",
            "gender_preference",
            # "age_from",
            # "age_to",
            "banned_countries",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        user = instance.user
        return response


class NotificationSerializer(serializers.ModelSerializer):
    profile_name = serializers.SerializerMethodField(method_name="get_name")
    message = serializers.SerializerMethodField(method_name="get_message")

    class Meta:
        model = Notification
        fields = ("id", "match", "profile_name", "message", "seen", )

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

    def get_message(self, obj):
        return "your profile is matched with %s" % self.get_name(obj)


class UnlikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unliked
        fields = ("id", "by", "user", "last_timestamp", )
