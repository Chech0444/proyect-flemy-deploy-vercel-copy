from rest_framework.permissions import BasePermission

from users.models import UserRole


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )

class IsPremiumUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in [UserRole.PREMIUM, UserRole.ADMIN])
        )
