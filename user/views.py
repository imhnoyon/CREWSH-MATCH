from django.db.models import Q
from django.contrib.auth import get_user_model

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
        photos = ImageSerializer(images, many=True, context={"request": self.request})
        return Response(photos.data, status=status.HTTP_201_CREATED)


class UpdatePhotos(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        serializer = UpdatePhotosSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        photos = ImageSerializer(self.request.user.images.all(), many=True, context={"request": self.request})
        return Response(photos.data, status=status.HTTP_201_CREATED)


class UploadProfilePhoto(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        photo = self.request.FILES.get("photo", None)
        user = self.request.user

        if photo:
            user.photo = photo
            user.save()

        return Response({"photo": user.get_photo()}, status=status.HTTP_201_CREATED)


class ViewUserDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        fields_to_exclude = ("email_address", "is_subscribed", "is_active",)

        for field in fields_to_exclude:
            data.pop(field)

        is_matched = (
                self.request.user.matches.filter(receiver=instance).exists() or
                self.request.user.accepted_matches.filter(sender=instance).exists())

        data["is_matched"] = is_matched

        return Response(data)


class Delete(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def delete(self, *args, **kwargs):
        User = get_user_model()
        User.objects.filter(id=self.request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
