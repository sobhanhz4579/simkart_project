# wishlist/permissions.py
from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or request.user == view.get_object().user)
