from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import generics
from rest_framework import  parsers
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from  .models import Profile
from .permissions import AccountOwner, ProfileOwner
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ForgotPasswordSerializer,
    ResendVerificationCodeSerializer,
    VerifyResetCodeSerializer,
    VerifyOptSerializerWithUserId,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    ImageSerializer,
    MultipleImageUploadSerializer,
    RefreshTokenSerializer
)


class Signup(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = {"user_id": serializer.data['user_id']}
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)


class ResendVerificationCode(generics.GenericAPIView):
    """
    Use this to resend otp code to specified email
    """
    serializer_class = ResendVerificationCodeSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmail(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, *args, **kwargs):
        serializer = VerifyOptSerializerWithUserId(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class Signin(TokenObtainPairView):
    serializer_class = AuthTokenSerializer


class ForgotPassword(generics.GenericAPIView):

    serializer_class = ForgotPasswordSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class VerifyResetCode(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = VerifyResetCodeSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(response, status=status.HTTP_200_OK)


class ChangePassword(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully", "success": True}, status=status.HTTP_200_OK)
    

class ResetPassword(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshToken(TokenRefreshView):
    serializer_class = RefreshTokenSerializer

    def get_serializer(self, *args, **kwargs):
        data = {"refresh": self.request.data.get("refresh_token")}
        super().get_serializer(data=data, *args, **kwargs)


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


class UpdateProfile(APIView):
    permission_classes = [AccountOwner, ]
    serializer_class = UserSerializer

    def post(self, *args, **kwargs):
        user = get_object_or_404(get_user_model(), id=self.kwargs.get("pk"))
        self.check_object_permissions(self.request, user)
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

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UploadPhotos(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, ]

    def post(self, *args, **kwargs):
        serializer = MultipleImageUploadSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        photos = ImageSerializer(images, many=True)
        return Response(photos.data, status=status.HTTP_201_CREATED)
