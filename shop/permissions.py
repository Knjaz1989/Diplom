from rest_framework.permissions import BasePermission


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        if request.user.type == "buyer":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True
        return False
