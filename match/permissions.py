from rest_framework.permissions import BasePermission


class IsRequestReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.user, obj.receiver)
        return bool(request.user.is_authenticated and request.user.pk == obj.receiver.pk)
