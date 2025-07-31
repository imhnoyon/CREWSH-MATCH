import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.inbox_id = self.scope["url_route"]["kwargs"]["inbox_id"]
        self.room_group_name = f"chat_{self.inbox_id}"
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()
    
    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.message",
                "payload": json.loads(text_data)
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
