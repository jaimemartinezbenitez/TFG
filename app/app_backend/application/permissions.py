from rest_framework import permissions

from .models import Collaboration


class IsOwnerOrReadOnlyCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        collaboration_filter = {'user': request.user}
        if obj.__class__.__name__ == 'Task':
            collaboration_filter['task'] = obj
        elif obj.__class__.__name__ == 'Project':
            collaboration_filter['project'] = obj
        else:
            return False

        collaboration = Collaboration.objects.filter(**collaboration_filter).first()
        if not collaboration:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return collaboration.role in ['EDITOR', 'ADMIN']


class IsOwnerUserData(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', None) == request.user
