from rest_framework import permissions

from .models import Collaboration, CollaborationStatus


class IsOwnerOrReadOnlyCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        if obj.__class__.__name__ == 'Task':
            collaboration = Collaboration.objects.filter(user=request.user, task=obj, status=CollaborationStatus.ACCEPTED).first()
            if not collaboration and obj.project_id:
                collaboration = Collaboration.objects.filter(user=request.user, project=obj.project, status=CollaborationStatus.ACCEPTED).first()
        elif obj.__class__.__name__ == 'Project':
            collaboration = Collaboration.objects.filter(user=request.user, project=obj, status=CollaborationStatus.ACCEPTED).first()
        else:
            return False

        if not collaboration:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return collaboration.role in ['EDITOR', 'ADMIN']


class IsOwnerUserData(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', None) == request.user
