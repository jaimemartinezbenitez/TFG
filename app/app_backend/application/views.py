import csv

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import (
    Achievement,
    Collaboration,
    Export,
    Metric,
    Notification,
    ProductivitySession,
    Project,
    Statistic,
    Task,
    TaskStatus,
)
from .permissions import IsOwnerOrReadOnlyCollaborator, IsOwnerUserData
from .serializers import (
    AchievementSerializer,
    CollaborationSerializer,
    ExportSerializer,
    MetricSerializer,
    NotificationSerializer,
    ProductivitySessionSerializer,
    ProjectSerializer,
    RegisterSerializer,
    StatisticSerializer,
    TaskSerializer,
    UserSerializer,
    build_metric_for_user,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyCollaborator]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()
        shared_projects = Collaboration.objects.filter(user=user, project__isnull=False).values('project_id')
        return Project.objects.filter(Q(owner=user) | Q(id__in=shared_projects)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyCollaborator]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        shared_tasks = Collaboration.objects.filter(user=user, task__isnull=False).values('task_id')
        shared_projects = Collaboration.objects.filter(user=user, project__isnull=False).values('project_id')
        return Task.objects.filter(
            Q(owner=user) | Q(id__in=shared_tasks) | Q(project_id__in=shared_projects)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = TaskStatus.COMPLETED
        task.save(update_fields=['status', 'updated_at'])
        self._assign_first_task_achievement(request.user)
        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        task = self.get_object()
        project_id = request.data.get('project')
        if not project_id:
            return Response({'project': 'Debes indicar el proyecto destino.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'project': 'El proyecto destino no existe.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, project)
        task.project = project
        task.save(update_fields=['project', 'updated_at'])
        return Response(TaskSerializer(task, context={'request': request}).data)

    def _assign_first_task_achievement(self, user):
        Achievement.objects.get_or_create(
            user=user,
            name='Primera tarea completada',
            defaults={'description': 'Has completado tu primera tarea.'},
        )


class CollaborationViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Collaboration.objects.none()
        if self.request.method not in permissions.SAFE_METHODS:
            return Collaboration.objects.filter(owner=user)
        return Collaboration.objects.filter(Q(owner=user) | Q(user=user))

    def perform_create(self, serializer):
        serializer.save()


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        return Response(NotificationSerializer(notification).data)


class ProductivitySessionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductivitySessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ProductivitySession.objects.none()
        return ProductivitySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        productivity_session = self.get_object()
        productivity_session.status = request.data.get('status', 'COMPLETED')
        productivity_session.end_at = timezone.now()
        if productivity_session.total_duration == 0:
            delta = productivity_session.end_at - productivity_session.start_at
            productivity_session.total_duration = max(int(delta.total_seconds() // 60), 0)
        productivity_session.save()
        return Response(ProductivitySessionSerializer(productivity_session).data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Achievement.objects.none()
        return Achievement.objects.filter(user=self.request.user)


class MetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Metric.objects.none()
        return Metric.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        metric = build_metric_for_user(request.user)
        return Response(MetricSerializer(metric).data, status=status.HTTP_201_CREATED)


class StatisticViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Statistic.objects.none()
        return Statistic.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExportViewSet(viewsets.ModelViewSet):
    serializer_class = ExportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Export.objects.none()
        return Export.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productividad.csv"'
        writer = csv.writer(response)
        writer.writerow(['usuario', 'email', 'tareas_creadas', 'tareas_completadas', 'minutos_efectivos'])
        metric = Metric.objects.filter(user=request.user).first() or build_metric_for_user(request.user)
        writer.writerow([
            request.user.username,
            request.user.email,
            metric.tasks_created,
            metric.tasks_completed,
            metric.effective_minutes,
        ])
        Export.objects.create(user=request.user, format='CSV', date_range=request.query_params.get('range', ''))
        return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calendar_view(request):
    user = request.user
    tasks = Task.objects.filter(owner=user, due_date__isnull=False)
    projects = Project.objects.filter(owner=user).filter(Q(start_date__isnull=False) | Q(end_date__isnull=False))
    items = [
        {
            'type': 'task',
            'id': task.id,
            'title': task.title,
            'date': task.due_date,
            'status': task.status,
            'priority': task.priority,
        }
        for task in tasks
    ]
    for project in projects:
        if project.start_date:
            items.append({'type': 'project_start', 'id': project.id, 'title': project.name, 'date': project.start_date})
        if project.end_date:
            items.append({'type': 'project_end', 'id': project.id, 'title': project.name, 'date': project.end_date})
    return Response(sorted(items, key=lambda item: item['date']))
