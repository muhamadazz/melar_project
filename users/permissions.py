from rest_framework import permissions # type: ignore

class IsAdmin(permissions.BasePermission):
    """Allow access only to users with the 'admin' role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsSeller(permissions.BasePermission):
    """Allow access only to users with the 'seller' role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'


class IsCustomer(permissions.BasePermission):
    """Allow access only to users with the 'customer' role."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'
    
class IsOwner(permissions.BasePermission):
    """Allow access only to the owner of the object."""
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user  # Sesuaikan dengan field yang tepat
