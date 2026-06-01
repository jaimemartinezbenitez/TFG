import csv
from datetime import timedelta
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Achievement,
    ChartType,
    Collaboration,
    CollaborationStatus,
    Export,
    Metric,
    Notification,
    ProductivitySession,
    Project,
    SessionStatus,
    Statistic,
    Task,
    TaskStatus,
)
from .permissions import IsOwnerOrReadOnlyCollaborator, IsOwnerUserData
from .serializers import (
    AccountDeleteSerializer,
    AchievementSerializer,
    ChangePasswordSerializer,
    CollaborationSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    ExportSerializer,
    LogoutSerializer,
    MetricSerializer,
    NotificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProductivitySessionSerializer,
    ProjectSerializer,
    RegisterSerializer,
    StatisticSerializer,
    TaskSerializer,
    UserSerializer,
    build_metric_for_user,
)


def _accessible_project_ids(user):
    return Collaboration.objects.filter(
        user=user,
        project__isnull=False,
        status=CollaborationStatus.ACCEPTED,
    ).values('project_id')


def _accessible_task_ids(user):
    return Collaboration.objects.filter(
        user=user,
        task__isnull=False,
        status=CollaborationStatus.ACCEPTED,
    ).values('task_id')


def accessible_projects(user):
    return Project.objects.filter(Q(owner=user) | Q(id__in=_accessible_project_ids(user))).distinct()


def accessible_tasks(user):
    return Task.objects.filter(
        Q(owner=user) | Q(id__in=_accessible_task_ids(user)) | Q(project_id__in=_accessible_project_ids(user))
    ).distinct()


def assign_productivity_achievements(user):
    completed_tasks = Task.objects.filter(owner=user, status=TaskStatus.COMPLETED).count()
    total_tasks = Task.objects.filter(owner=user).count()
    completed_sessions = ProductivitySession.objects.filter(user=user, status=SessionStatus.COMPLETED).count()
    effective_minutes = ProductivitySession.objects.filter(user=user).aggregate(
        total=Sum('effective_time')
    )['total'] or 0

    rules = [
        (completed_tasks >= 1, 'Primera tarea completada', 'Has completado tu primera tarea.'),
        (completed_tasks >= 5, 'Cinco tareas completadas', 'Has completado cinco tareas.'),
        (total_tasks >= 10, 'Planificador constante', 'Has creado diez tareas en la plataforma.'),
        (completed_sessions >= 1, 'Primera sesion productiva', 'Has finalizado una sesion de productividad.'),
        (effective_minutes >= 120, 'Dos horas enfocadas', 'Has registrado al menos dos horas efectivas.'),
    ]
    created = []
    for condition, name, description in rules:
        if condition:
            achievement, was_created = Achievement.objects.get_or_create(
                user=user,
                name=name,
                defaults={'description': description},
            )
            if was_created:
                created.append(achievement)
    return created


def generate_task_reminders(user):
    today = timezone.localdate()
    thresholds = {
        'HIGH': 3,
        'MEDIUM': 2,
        'LOW': 1,
    }
    tasks = Task.objects.filter(owner=user, due_date__isnull=False).exclude(
        status__in=[TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    )
    created = []
    for task in tasks:
        days_left = (task.due_date - today).days
        if days_left < 0:
            message = f'La tarea "{task.title}" esta vencida desde {task.due_date}.'
        elif days_left <= thresholds.get(task.priority, 1):
            message = f'La tarea "{task.title}" vence en {days_left} dia(s). Prioridad: {task.priority}.'
        else:
            continue
        notification, was_created = Notification.objects.get_or_create(
            user=user,
            task=task,
            message=message,
            defaults={'event_date': timezone.now()},
        )
        if was_created:
            created.append(notification)
    return created


def parse_period(request):
    view = request.query_params.get('view', 'month').lower()
    selected_date = parse_date(request.query_params.get('date', '')) or timezone.localdate()
    if view == 'day':
        start_date = selected_date
        end_date = selected_date
    elif view == 'week':
        start_date = selected_date - timedelta(days=selected_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif view == 'month':
        start_date = selected_date.replace(day=1)
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    else:
        return None, None, None, Response(
            {'view': 'El valor debe ser day, week o month.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return view, start_date, end_date, None


def parse_date_range(request):
    start_param = request.query_params.get('start')
    end_param = request.query_params.get('end')
    if not start_param and not end_param:
        return None, None, None
    start_date = parse_date(start_param or '')
    end_date = parse_date(end_param or '')
    if not start_date or not end_date:
        return None, None, Response(
            {'range': 'Debes indicar start y end con formato YYYY-MM-DD.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if end_date < start_date:
        return None, None, Response(
            {'range': 'La fecha end no puede ser anterior a start.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return start_date, end_date, None


def escape_pdf_text(value):
    return str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def build_simple_pdf(lines):
    content = ['BT', '/F1 12 Tf', '50 760 Td']
    for index, line in enumerate(lines[:38]):
        if index:
            content.append('0 -18 Td')
        content.append(f'({escape_pdf_text(line)}) Tj')
    content.append('ET')
    stream = '\n'.join(content).encode('latin-1', errors='replace')
    objects = [
        b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
        b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
        b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
        b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
        b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
        b'5 0 obj << /Length ' + str(len(stream)).encode() + b' >> stream\n' + stream + b'\nendstream endobj',
    ]
    pdf = bytearray(b'%PDF-1.4\n')
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj + b'\n')
    xref_offset = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode())
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode())
    pdf.extend(
        f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_offset}\n%%EOF\n'.encode()
    )
    return bytes(pdf)


class EmailOrUsernameTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_model().objects.filter(is_active=True).exclude(pk=self.request.user.pk).order_by('username')


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Contrasena actualizada correctamente.'})


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Sesion cerrada correctamente.'}, status=status.HTTP_200_OK)


class AccountDeleteView(generics.GenericAPIView):
    serializer_class = AccountDeleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if settings.EMAIL_BACKEND.endswith('smtp.EmailBackend') and not settings.EMAIL_HOST:
            return Response(
                {'email': 'El servidor SMTP no esta configurado. Define EMAIL_HOST en las variables de entorno.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        reset_token = serializer.save()
        confirm_endpoint = request.build_absolute_uri('/api/auth/password-reset/confirm/')
        try:
            send_mail(
                'Restablecimiento de contrasena',
                (
                    'Has solicitado restablecer la contrasena de tu cuenta.\n\n'
                    f'Token: {reset_token.token}\n'
                    f'Endpoint de confirmacion: {confirm_endpoint}\n'
                    f'Caduca: {reset_token.expires_at}\n\n'
                    'Si no has solicitado este cambio, puedes ignorar este mensaje.'
                ),
                settings.DEFAULT_FROM_EMAIL,
                [serializer.validated_data['email']],
                fail_silently=False,
            )
        except (OSError, SMTPException):
            reset_token.mark_as_used()
            return Response(
                {'email': 'No se pudo enviar el correo de recuperacion. Revisa la configuracion SMTP.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {'detail': 'Se ha enviado un correo con las instrucciones de recuperacion.'},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Contrasena actualizada correctamente.'})


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyCollaborator]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()
        return accessible_projects(user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyCollaborator]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return accessible_tasks(user)

    def perform_create(self, serializer):
        task = serializer.save(owner=self.request.user)
        if task.status == TaskStatus.COMPLETED:
            assign_productivity_achievements(self.request.user)
        generate_task_reminders(self.request.user)

    def perform_update(self, serializer):
        previous_status = serializer.instance.status
        task = serializer.save()
        if previous_status != TaskStatus.COMPLETED and task.status == TaskStatus.COMPLETED:
            assign_productivity_achievements(self.request.user)
        generate_task_reminders(self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = TaskStatus.COMPLETED
        task.save(update_fields=['status', 'updated_at'])
        achievements = assign_productivity_achievements(request.user)
        data = TaskSerializer(task, context={'request': request}).data
        data['new_achievements'] = AchievementSerializer(achievements, many=True).data
        return Response(data)

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


class CollaborationViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Collaboration.objects.none()
        if self.request.method not in permissions.SAFE_METHODS:
            queryset = Collaboration.objects.filter(Q(owner=user) | Q(user=user))
        else:
            queryset = Collaboration.objects.filter(Q(owner=user) | Q(user=user))

        resource_type = self.request.query_params.get('resource_type')
        task_id = self.request.query_params.get('task')
        project_id = self.request.query_params.get('project')

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.select_related('user', 'owner', 'task', 'project')

    def perform_create(self, serializer):
        collaboration = serializer.save(owner=self.request.user, status=CollaborationStatus.PENDING)
        resource = collaboration.task or collaboration.project
        resource_name = getattr(resource, 'title', None) or getattr(resource, 'name', 'recurso')
        Notification.objects.create(
            user=collaboration.user,
            task=collaboration.task,
            project=collaboration.project,
            message=f'{collaboration.owner.username} te ha invitado a colaborar en "{resource_name}".',
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        collaboration = self.get_object()
        if collaboration.user != request.user:
            return Response({'detail': 'Solo el usuario invitado puede aceptar esta colaboracion.'}, status=status.HTTP_403_FORBIDDEN)
        collaboration.status = CollaborationStatus.ACCEPTED
        collaboration.save(update_fields=['status'])
        return Response(self.get_serializer(collaboration).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        collaboration = self.get_object()
        if collaboration.user != request.user:
            return Response({'detail': 'Solo el usuario invitado puede rechazar esta colaboracion.'}, status=status.HTTP_403_FORBIDDEN)
        collaboration.status = CollaborationStatus.REJECTED
        collaboration.save(update_fields=['status'])
        return Response(self.get_serializer(collaboration).data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def list(self, request, *args, **kwargs):
        generate_task_reminders(request.user)
        return super().list(request, *args, **kwargs)

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

    @action(detail=False, methods=['post'])
    def generate_reminders(self, request):
        notifications = generate_task_reminders(request.user)
        return Response({
            'created': len(notifications),
            'notifications': NotificationSerializer(notifications, many=True).data,
        })


class ProductivitySessionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductivitySessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ProductivitySession.objects.none()
        return ProductivitySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        productivity_session = serializer.save(user=self.request.user)
        if productivity_session.status == SessionStatus.COMPLETED:
            assign_productivity_achievements(self.request.user)

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        productivity_session = self.get_object()
        requested_status = request.data.get('status', SessionStatus.COMPLETED)
        if requested_status not in [SessionStatus.COMPLETED, SessionStatus.INTERRUPTED]:
            return Response({'status': 'Debe ser COMPLETED o INTERRUPTED.'}, status=status.HTTP_400_BAD_REQUEST)

        for field in ['total_duration', 'effective_time', 'completed_cycles']:
            if field in request.data:
                try:
                    value = int(request.data[field])
                except (TypeError, ValueError):
                    return Response({field: 'Debe ser un numero entero.'}, status=status.HTTP_400_BAD_REQUEST)
                if value < 0:
                    return Response({field: 'No puede ser negativo.'}, status=status.HTTP_400_BAD_REQUEST)
                setattr(productivity_session, field, value)

        if 'configuration' in request.data:
            configuration = request.data.get('configuration')
            if not isinstance(configuration, dict):
                return Response({'configuration': 'La configuracion debe ser un objeto JSON.'}, status=status.HTTP_400_BAD_REQUEST)
            productivity_session.configuration = configuration

        productivity_session.status = requested_status
        productivity_session.end_at = timezone.now()
        if productivity_session.total_duration == 0:
            delta = productivity_session.end_at - productivity_session.start_at
            productivity_session.total_duration = max(int(delta.total_seconds() // 60), 0)
        if productivity_session.effective_time == 0 and requested_status == SessionStatus.COMPLETED:
            productivity_session.effective_time = productivity_session.total_duration
        productivity_session.save()
        achievements = assign_productivity_achievements(request.user)
        data = ProductivitySessionSerializer(productivity_session).data
        data['new_achievements'] = AchievementSerializer(achievements, many=True).data
        return Response(data)


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
        assign_productivity_achievements(request.user)
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

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user
        tasks = Task.objects.filter(owner=user)
        projects = Project.objects.filter(owner=user)
        sessions = ProductivitySession.objects.filter(user=user)
        metric = Metric.objects.filter(user=user).first() or build_metric_for_user(user)

        tasks_by_status = {
            row['status']: row['total']
            for row in tasks.values('status').annotate(total=Count('id')).order_by('status')
        }
        tasks_by_priority = {
            row['priority']: row['total']
            for row in tasks.values('priority').annotate(total=Count('id')).order_by('priority')
        }
        sessions_by_technique = {
            row['technique']: row['total']
            for row in sessions.values('technique').annotate(total=Sum('effective_time')).order_by('technique')
        }
        project_progress = []
        for project in projects:
            project_tasks = project.tasks.filter(owner=user)
            total = project_tasks.count()
            completed = project_tasks.filter(status=TaskStatus.COMPLETED).count()
            project_progress.append({
                'project_id': project.id,
                'project': project.name,
                'tasks': total,
                'completed': completed,
                'progress_percentage': round((completed / total * 100) if total else 0, 2),
            })

        visual_data = {
            'metric': MetricSerializer(metric).data,
            'tasks_by_status': tasks_by_status,
            'tasks_by_priority': tasks_by_priority,
            'sessions_by_technique': sessions_by_technique,
            'project_progress': project_progress,
        }
        Statistic.objects.create(
            user=user,
            metric=metric,
            chart_type=ChartType.BAR,
            visual_data=visual_data,
        )
        return Response(visual_data)


class ExportViewSet(viewsets.ModelViewSet):
    serializer_class = ExportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerUserData]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Export.objects.none()
        return Export.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def export_lines(self, request):
        start_date, end_date, error = parse_date_range(request)
        if error:
            return None, error
        metric = Metric.objects.filter(user=request.user).first() or build_metric_for_user(request.user)
        tasks = Task.objects.filter(owner=request.user)
        sessions = ProductivitySession.objects.filter(user=request.user)
        if start_date and end_date:
            tasks = tasks.filter(created_at__date__range=(start_date, end_date))
            sessions = sessions.filter(start_at__date__range=(start_date, end_date))

        lines = [
            f'Usuario: {request.user.username}',
            f'Email: {request.user.email}',
            f'Tareas creadas: {metric.tasks_created}',
            f'Tareas completadas: {metric.tasks_completed}',
            f'Minutos efectivos: {metric.effective_minutes}',
            f'Progreso: {metric.progress_percentage}%',
            '',
            'Tareas:',
        ]
        lines.extend([
            f'- {task.title} | {task.status} | {task.priority} | limite: {task.due_date or "sin fecha"}'
            for task in tasks.order_by('due_date', 'title')
        ])
        lines.append('')
        lines.append('Sesiones:')
        lines.extend([
            f'- {session.technique} | {session.status} | {session.effective_time} minutos'
            for session in sessions.order_by('-start_at')
        ])
        return lines, None

    @action(detail=False, methods=['get'])
    def csv(self, request):
        lines, error = self.export_lines(request)
        if error:
            return error
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productividad.csv"'
        writer = csv.writer(response)
        for line in lines:
            writer.writerow([line])
        Export.objects.create(user=request.user, format='CSV', date_range=request.query_params.get('range', ''))
        return response

    @action(detail=False, methods=['get'])
    def pdf(self, request):
        lines, error = self.export_lines(request)
        if error:
            return error
        response = HttpResponse(build_simple_pdf(lines), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="productividad.pdf"'
        Export.objects.create(user=request.user, format='PDF', date_range=request.query_params.get('range', ''))
        return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calendar_view(request):
    view, start_date, end_date, error = parse_period(request)
    if error:
        return error
    user = request.user
    tasks = accessible_tasks(user).filter(due_date__range=(start_date, end_date))
    projects = accessible_projects(user).filter(
        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date))
    )
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
        if project.start_date and start_date <= project.start_date <= end_date:
            items.append({'type': 'project_start', 'id': project.id, 'title': project.name, 'date': project.start_date})
        if project.end_date and start_date <= project.end_date <= end_date:
            items.append({'type': 'project_end', 'id': project.id, 'title': project.name, 'date': project.end_date})
    return Response({
        'view': view,
        'start_date': start_date,
        'end_date': end_date,
        'items': sorted(items, key=lambda item: item['date']),
    })
