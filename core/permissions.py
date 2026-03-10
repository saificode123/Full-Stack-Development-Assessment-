from rest_framework import permissions

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of a team to delete or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD or OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write/Delete permissions are only allowed to the creator
        return obj.creator == request.user