from rest_framework import permissions

class IsTeamCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission class to enforce role-based access control (RBAC).
    
    Rules:
    - Any authenticated user can view the team details (GET, HEAD, OPTIONS).
    - ONLY the user who created the team can modify or delete it (PUT, PATCH, DELETE).
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write/Delete permissions are only allowed to the creator of the team.
        # This satisfies the assessment bonus feature.
        # It assumes your Team model has a 'creator' field linked to the User.
        return obj.creator == request.user