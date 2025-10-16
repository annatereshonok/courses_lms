from rest_framework.permissions import BasePermission


def is_moderator(user) -> bool:
    return user.is_authenticated and user.groups.filter(name="moderators").exists()


class ModeratorPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.groups.filter(name="moderators").exists()


class OwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
