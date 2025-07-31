from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from content.serializers import PhotoSerializer

from .models import Inbox
from .serializers import MessageSerializer, BaseMultiplePhotoMessageSerializer


class SendMessage(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [JSONParser, MultiPartParser, FormParser, ]

    def get_object(self):
        return get_object_or_404(Inbox, inbox_id=self.kwargs.get("inbox_id"))

    def post(self, *args, **kwargs):
        serializer = MessageSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        channel_layer = get_channel_layer()
        group_name = f"chat_{self.kwargs.get("inbox_id")}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat.message",
                "payload": serializer.data
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class SendMultiplePhoto(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, ]

    def post(self, *args, **kwargs):
        photos = self.request.FILES.getlist("content_data")
        response = []

        for photo in photos:
            photo_serializer = PhotoSerializer(data={"photo": photo})
            photo_serializer.is_valid()
            uploaded_photo = photo_serializer.save()
            
            payload = {
                "inbox": self.request.data.get("inbox"),
                "sender": self.request.data.get("sender"),
                "receiver": self.request.data.get("receiver"),
                "object_id": uploaded_photo.id,
                "message_type": "Photo"
            }
            
            serializer = BaseMultiplePhotoMessageSerializer(data=payload)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response.append(serializer.data)
            
            channel_layer = get_channel_layer()
            group_name = f"chat_{self.kwargs.get("inbox_id")}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat.message",
                    "payload": serializer.data
                }
            )
        

        return Response(response)

