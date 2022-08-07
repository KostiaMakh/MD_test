from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allow access only for admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)
