from rest_framework import permissions


class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to admin,

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_superuser

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
