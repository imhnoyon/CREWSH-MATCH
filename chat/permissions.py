from rest_framework.permissions import BasePermission


class HasInboxAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        match = obj.match
        users = (match.sender, match.receiver)
        return bool(request.user.is_authenticated and request.user in users)

