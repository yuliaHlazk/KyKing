from rest_framework import permissions
from users_app.models import UserProfile


class RoleRequired(permissions.BasePermission):

    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)
        if not profile:
            return False

        return profile.role in self.allowed_roles


class IsAuthorOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        if profile and profile.role == UserProfile.Role.ADMIN:
            return True

        return obj.author == request.user


class IsFavoriteOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == UserProfile.Role.ADMIN:
            return True

        return obj.user == request.user


class IsChefOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        return profile and profile.role in [
            UserProfile.Role.CHEF,
            UserProfile.Role.ADMIN,
        ]
