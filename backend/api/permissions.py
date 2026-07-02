"""
Role-based DRF permissions reusing the existing accounts role/group system
(UserProfile.role: admin/teacher/student/parent). No new role system invented.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


def _role(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and (request.user.is_superuser or _role(request.user) == 'admin'))


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and (request.user.is_superuser
                         or _role(request.user) in {'admin', 'teacher'}))


class ReadOnlyOrTeacher(BasePermission):
    """Everyone authenticated can read; only teacher/admin can write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _role(request.user) in {'admin', 'teacher'}
