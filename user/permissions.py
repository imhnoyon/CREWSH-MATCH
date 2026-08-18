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
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        profile = Profile.objects.filter(user=request.user)

        return bool(profile.exists())
