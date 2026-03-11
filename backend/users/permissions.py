from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to get profile info.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.id == request.user.id
