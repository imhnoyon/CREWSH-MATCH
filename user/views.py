from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import generics
from rest_framework import  parsers
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from  .models import Profile
from .permissions import AccountOwner, ProfileRequired
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ImageSerializer,
    MultipleImageUploadSerializer,
    UpdatePhotosSerializer,
)

class UpdateUser(generics.UpdateAPIView):
    permission_classes = [AccountOwner, ]
    serializer_class = UserSerializer
    lookup_field = "pk"
    queryset = get_user_model().objects.all()


class RetrieveProfile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ProfileRequired]
    serializer_class = UserSerializer

    def get(self, *args, **kwargs):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfile(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def post(self, *args, **kwargs):
        user = self.request.user
        serializer = ProfileSerializer(data=self.request.data)

        profile = Profile.objects.filter(user=user)

        if profile.exists():
            serializer = ProfileSerializer(instance=profile.first(), data=self.request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        full_name = self.request.data.get("full_name")

        if full_name and user.full_name != full_name:
            user.full_name = full_name
            user.save()

        user_serializer = UserSerializer(user)

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class UploadPhotos(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        serializer = MultipleImageUploadSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        photos = ImageSerializer(images, many=True)
        return Response(photos.data, status=status.HTTP_201_CREATED)


class UpdatePhotos(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        serializer = UpdatePhotosSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        photos = ImageSerializer(self.request.user.images.all(), many=True)
        return Response(photos.data, status=status.HTTP_201_CREATED)
