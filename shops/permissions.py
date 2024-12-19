from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Permission untuk memastikan hanya pemilik toko yang dapat melakukan perubahan.
    User lain hanya dapat membaca (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS mencakup GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        # Hanya owner yang dapat mengubah data
        return obj.user == request.user
