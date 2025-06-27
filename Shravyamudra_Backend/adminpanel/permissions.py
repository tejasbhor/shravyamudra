from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """Allows access only to users with admin role or Django superuser."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (getattr(request.user, 'role', None) == 'admin' or request.user.is_superuser))
