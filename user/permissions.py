from rest_framework.permissions import BasePermission

from .models import Profile


class AccountOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.pk == obj.pk)


class ProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.pk == obj.user.pk)


class ProfileRequired(BasePermission):
    message = "Please create your profile first"
    def has_permission(self, request, view):
        profile = Profile.objects.filter(user=request.user)
        return bool(request.user.is_authenticated and profile.exists())
