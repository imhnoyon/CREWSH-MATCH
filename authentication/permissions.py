from rest_framework.permissions import BasePermission


class AccountOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.pk == obj.pk)


class ProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.pk == obj.user.pk)

