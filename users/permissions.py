from rest_framework.permissions import BasePermission


class IsSelfUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user and (user.is_staff or obj.pk == user.pk)
