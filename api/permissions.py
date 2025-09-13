from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow admin users to edit, anyone to read."""

    def has_permission(self, request, view) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
        ) or request.user.is_staff


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """Allow owners/admins to edit, others to read only."""

    def has_object_permission(self, request, view, obj) -> bool:
        is_owner = False
        if hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        else:
            is_owner = obj == request.user

        return (request.method in permissions.SAFE_METHODS or
                is_owner or request.user.is_staff)
