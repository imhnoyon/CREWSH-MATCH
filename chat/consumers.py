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
            self.close()
            
        self.inbox_id = self.scope["url_route"]["kwargs"]["inbox_id"]

        try:
            self.inbox = Inbox.objects.get(inbox_id=self.inbox_id)
        except Inbox.DoesNotExist:
            print("No such inbox_id")
            self.close()

        self.room_group_name = f"chat_{self.inbox_id}"
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.connect_user_to_inbox()
        # print(f"{self.user} is connected")
        self.accept()
    
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
        self.inbox.online_users.remove(self.user)

    def disconnect(self, code):
        self.disconnect_user_from_inbox()
        # print(f"{self.user} is disconnected")
        super().disconnect(code)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
