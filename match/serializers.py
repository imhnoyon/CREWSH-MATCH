from django.db.models import Q
from django.conf import settings
from rest_framework import serializers

from user.models import Profile
from .models import Request, Match, Notification, Unliked


class RequestSerializer(serializers.ModelSerializer):
    match = None
    class Meta:
        model = Request
        fields = ("id", "sender", "receiver", )
        read_only_fields = ("sender", )

    def validate(self, attrs):
        request = self.context.get("request")
        sender = request.user
        receiver = attrs['receiver']

        if sender == receiver:
            raise serializers.ValidationError({"message": "You cannot send a request to yourself."})

        if Request.objects.filter(
                Q(sender=sender, receiver=receiver) |
                Q(sender=receiver, receiver=sender)
        ).exists():
            raise serializers.ValidationError({"message": "You have already sent a request to this user."})

        return attrs

    def create(self, validated_data):
        self.match = None
        request = self.context.get("request")
        sender = request.user
        receiver = validated_data['receiver']

        # Check if the receiver already liked the sender
        request_obj = Request.objects.filter(
            sender=receiver,
            receiver=sender,
            accepted=False,
            canceled=False
        ).first()

        if request_obj:
            request_obj.accepted = True
            request_obj.save()
            match, _ = Match.objects.get_or_create(sender=receiver, receiver=sender)
            self.match = match
        else:
            request_obj = Request.objects.create(sender=sender, receiver=receiver)

        return request_obj

    def to_representation(self, instance):
        context = super().to_representation(instance)
        sender = instance.sender
        receiver = instance.receiver
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo(), "age": sender.profile.age}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo(), "age": receiver.profile.age}
        context['is_a_match'] = instance.accepted

        if self.match:
            context['inbox_id'] = self.match.inbox.inbox_id

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
        print("match", instance, instance.id)
        inbox = instance.inbox
        context['sender'] = {"id": sender.id, "full_name": sender.full_name, "photo": sender.get_photo(), "age": sender.profile.age}
        context['receiver'] = {"id": receiver.id, "full_name": receiver.full_name, "photo": receiver.get_photo(), "age": receiver.profile.age}
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
        response['photo'] = user.get_photo()
        response['images'] = [ {"url": f"{settings.DOMAIN}{image.image.url}"} for image in user.images.all()]
        response['age'] = instance.age
        response['is_private'] = instance.user.is_private
        response['is_subscribed'] = instance.user.is_subscribed
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
