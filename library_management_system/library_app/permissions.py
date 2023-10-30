from rest_framework import permissions

from library_app.models import Roles


class IsAdmin(permissions.BasePermission):
    """Custom permission to only allow admin to make changes."""

    def has_permission(self, request, view):
        """Checks if the Admin has the permission."""
        user = request.user
        return (
            user.is_authenticated and user.has_role(Roles.ADMIN)
        ) or permissions.IsAdminUser


class IsLibrarian(permissions.BasePermission):
    """Custom permission to only allow librarian to make changes"""

    def has_permission(self, request, view):
        """Checks if the user is a librarian."""
        user = request.user
        return user.is_authenticated and user.has_role(Roles.LIBRARIAN)


class BookPermission(permissions.BasePermission):
    """Custom permission to allow actions on books only for librarians"""

    def has_permission(self, request, view):
        """Checks if the user has permission to perform actions on books."""

        if view.action in ["list", "retrieve"]:
            return True
        return IsLibrarian().has_permission(request, view)


class RequestPermission(permissions.BasePermission):
    """Custom permission to allow authenticated user to issue books"""

    def has_permission(self, request, view):
        """Checks if the user has permission to perform actions on issued books."""
        user = request.user

        if view.action in ["list", "retrieve", "partial_update"]:
            return user.is_authenticated and (
                user.has_role(Roles.USER) or user.has_role(Roles.LIBRARIAN)
            )
        return user.is_authenticated and user.has_role(Roles.USER)


class UserHandlePermission(permissions.BasePermission):
    """Custom permission for user handling"""

    def has_object_permission(self, request, view, obj):
        """Checks if the user has permission to perform actions on user object."""
        user = request.user

        if view.action in ["list", "retrieve", "update", "destroy"]:
            return user.is_authenticated and obj.username == user.username
        return False

    def has_permission(self, request, view):
        """Checks if the user has permission to create user or not."""
        user = request.user

        if view.action == "create":
            return not user.is_authenticated
        return True
