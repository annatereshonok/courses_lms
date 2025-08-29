from rest_framework.permissions import BasePermission


def is_moderator(user) -> bool:
    return user.is_authenticated and user.groups.filter(name='moderators').exists()


class ModeratorPermission(BasePermission):
    def has_permission(self, request, view):
        if is_moderator(request.user) and request.method in ('POST', 'DELETE'):
            return False
        return True


class OwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return True

        owner = getattr(obj, 'owner', None)
        if owner is None and hasattr(obj, 'course'):
            owner = getattr(obj.course, 'owner', None)
        return owner == request.user
