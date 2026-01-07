import json

from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Inbox
from .serializers import MessageSerializer


User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            self.close(code=401, reason="Authentication Failed")
            return
            
        self.inbox_id = self.scope["url_route"]["kwargs"]["inbox_id"]
        self.room_group_name = f"chat_{self.inbox_id}"

        # Check the existence of the inbox
        try:
            self.inbox = Inbox.objects.get(inbox_id=self.inbox_id)
        except Inbox.DoesNotExist:
            print("No such inbox_id")
            self.close(code=404, reason="Inbox id not valid")

        match = self.inbox.match
        inbox_users = (match.sender, match.receiver)

        # Check if the user is a member of the inbox
        if self.user not in inbox_users:
            self.close(code=401, reason="You are not permitted to access this inbox")

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.connect_user_to_inbox()
        # print(f"{self.user} is connected")

        self.accept()

        self.send_data_on_open_close(is_online=True)
    
    def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data)
        serializer = MessageSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()
            response = {
                "type": "chat.message",
                "success": True,
                "data": serializer.data
            }
        else:
            response = {
                "type": "chat.message",
                "success": False,
                "data": serializer.errors
            }
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, response)

    def connect_user_to_inbox(self):
        self.inbox.online_users.add(self.user)

    def disconnect_user_from_inbox(self):
        if self.user in self.inbox.online_users.all():
            self.inbox.online_users.remove(self.user)

    def send_data_on_open_close(self, is_online):
        event = {
            "type": "chat.presence",
            "user": self.user.full_name,
            "success": is_online,
            "online_users_id": [ user.id for user in self.inbox.online_users.all()]
        }
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, event)

    def chat_presence(self, event):
        self.send(text_data=json.dumps(event))

    def disconnect(self, code):
        if self.user.is_authenticated:
            self.disconnect_user_from_inbox()
            self.send_data_on_open_close(is_online=False)
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
        return super().disconnect(code)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
        self.update_inbox(event)

    def update_inbox(self, event: dict):
        user_ids = (self.inbox.match.sender.id, self.inbox.match.receiver.id)

        for user_id in user_ids:
            async_to_sync(self.channel_layer.group_send)(f"chat_{user_id}", event)


class InboxConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        if self.user.id != self.user_id:
            self.close(code=403, reason="You don't have permission to access this socket channel")

        self.room_group_name = f"chat_{self.user_id}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, json.loads(text_data))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
