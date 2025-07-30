from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import generics
from rest_framework import  parsers
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

from  .models import Profile
from .permissions import AccountOwner, ProfileOwner
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    SendOtpSerializer,
    OptSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    ImageSerializer,
    MultipleImageUploadSerializer
)


class CreateUser(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
 

class AuthToken(TokenObtainPairView):
    serializer_class = AuthTokenSerializer


class SendOtp(generics.GenericAPIView):
    """
    Use this to resend otp code to specified email
    """
    serializer_class = SendOtpSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {'message': "Otp sent !", 'success': True}
        return Response(response, status=status.HTTP_200_OK)


class VerifyOtp(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, *args, **kwargs):
        serializer = OptSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
    

class ChangePassword(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully", "success": True}, status=status.HTTP_200_OK)
    

class ConfirmPasswordReset(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful", "success": True}, status=status.HTTP_200_OK)


class UpdateUser(generics.UpdateAPIView):
    permission_classes = [AccountOwner, ]
    serializer_class = UserSerializer
    lookup_field = "pk"
    queryset = get_user_model().objects.all()


class RetrieveProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [AccountOwner, ]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        profile = instance.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfile(generics.UpdateAPIView):
    permission_classes = [ProfileOwner, ]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        profile = get_object_or_404(Profile, id=self.request.user.id)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(profile, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            profile._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadPhotos(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        serializer = MultipleImageUploadSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        photos = ImageSerializer(images, many=True)
        return Response(photos.data, status=status.HTTP_201_CREATED)
