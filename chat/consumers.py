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

        if not self.user.is_authenticated:
            self.close(code=401, reason="Authentication Failed")
            
        self.inbox_id = self.scope["url_route"]["kwargs"]["inbox_id"]
        self.room_group_name = f"chat_{self.inbox_id}"

        try:
            self.inbox = Inbox.objects.get(inbox_id=self.inbox_id)
        except Inbox.DoesNotExist:
            print("No such inbox_id")
            self.close(code=404, reason="Inbox id not valid")


        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.connect_user_to_inbox()
        # print(f"{self.user} is connected")

        self.accept()

        self.send_data_on_open_close(is_online=True)
    
    def receive(self, text_data):
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
            "status": is_online,
            "online_users_id": [ user.id for user in self.inbox.online_users.all()]
        }
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, event)

    def chat_presence(self, event):
        self.send(text_data=json.dumps(event))

    def disconnect(self, code):
        self.disconnect_user_from_inbox()
        # print(f"{self.user} is disconnected")
        self.send_data_on_open_close(is_online=False)
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
        super().disconnect(code)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
