import csv
from calendar import monthrange
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
    ProductivityTechnique,
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
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    year_start = today.replace(month=1, day=1)
    year_end = today.replace(month=12, day=31)

    user_tasks = Task.objects.filter(owner=user)
    completed_task_queryset = user_tasks.filter(status=TaskStatus.COMPLETED)
    completed_tasks = completed_task_queryset.count()
    total_tasks = user_tasks.count()
    completed_session_queryset = ProductivitySession.objects.filter(user=user, status=SessionStatus.COMPLETED)
    completed_sessions = completed_session_queryset.count()
    completed_pomodoros = completed_session_queryset.filter(technique=ProductivityTechnique.POMODORO).count()
    effective_minutes = ProductivitySession.objects.filter(user=user).aggregate(
        total=Sum('effective_time')
    )['total'] or 0

    def completed_tasks_between(start_date, end_date):
        return completed_task_queryset.filter(updated_at__date__range=(start_date, end_date)).count()

    def effective_minutes_between(start_date, end_date):
        return completed_session_queryset.filter(start_at__date__range=(start_date, end_date)).aggregate(
            total=Sum('effective_time')
        )['total'] or 0

    def active_days_between(start_date, end_date):
        return completed_session_queryset.filter(
            start_at__date__range=(start_date, end_date)
        ).values('start_at__date').distinct().count()

    weekly_completed_tasks = completed_tasks_between(week_start, week_end)
    weekly_effective_minutes = effective_minutes_between(week_start, week_end)
    weekly_active_days = active_days_between(week_start, week_end)
    monthly_completed_tasks = completed_tasks_between(month_start, month_end)
    monthly_effective_minutes = effective_minutes_between(month_start, month_end)
    monthly_active_days = active_days_between(month_start, month_end)
    yearly_completed_tasks = completed_tasks_between(year_start, year_end)
    yearly_effective_minutes = effective_minutes_between(year_start, year_end)
    yearly_active_days = active_days_between(year_start, year_end)

    latest_productivity_date = completed_session_queryset.order_by('-start_at').values_list(
        'start_at__date',
        flat=True,
    ).first() or today
    consecutive_days = consecutive_productivity_days(user, latest_productivity_date)
    early_completed_tasks = completed_task_queryset.filter(updated_at__hour__lt=8).exists()
    intense_pomodoro_day = completed_session_queryset.filter(
        technique=ProductivityTechnique.POMODORO,
    ).values('start_at__date').annotate(total=Count('id')).filter(total__gte=4).exists()

    rules = [
        (completed_tasks >= 1, 'Primeros pasos', 'Completa tu primera tarea.'),
        (completed_pomodoros >= 10, 'Enfoque total', 'Completa 10 sesiones Pomodoro.'),
        (consecutive_days >= 7, 'Constante', '7 dias seguidos activo.'),
        (completed_tasks >= 50, 'Productivo', 'Completa 50 tareas.'),
        (early_completed_tasks, 'Madrugador', 'Completa tareas antes de las 8am.'),
        (intense_pomodoro_day, 'Maratonista', '4 sesiones Pomodoro en un dia.'),
        (consecutive_days >= 30, 'Imparable', '30 dias seguidos activo.'),
        (completed_tasks >= 100, 'Experto', 'Completa 100 tareas.'),
        (completed_tasks >= 5, 'Cinco tareas completadas', 'Has completado cinco tareas.'),
        (total_tasks >= 10, 'Planificador constante', 'Has creado diez tareas en la plataforma.'),
        (completed_sessions >= 1, 'Primera sesion productiva', 'Has finalizado una sesion de productividad.'),
        (effective_minutes >= 120, 'Dos horas enfocadas', 'Has registrado al menos dos horas efectivas.'),
        (weekly_completed_tasks >= 1, 'Semana en marcha', 'Completa una tarea esta semana.'),
        (weekly_completed_tasks >= 5, 'Sprint semanal', 'Completa 5 tareas esta semana.'),
        (weekly_effective_minutes >= 180, 'Semana enfocada', 'Acumula 3 horas de enfoque esta semana.'),
        (weekly_active_days >= 5, 'Ritmo semanal', 'Registra sesiones en 5 dias de la semana.'),
        (monthly_completed_tasks >= 5, 'Mes activo', 'Completa 5 tareas este mes.'),
        (monthly_completed_tasks >= 20, 'Mes productivo', 'Completa 20 tareas este mes.'),
        (monthly_effective_minutes >= 900, 'Mes de enfoque', 'Acumula 15 horas de enfoque este mes.'),
        (monthly_active_days >= 15, 'Constancia mensual', 'Registra sesiones en 15 dias del mes.'),
        (yearly_active_days >= 60, 'Ano constante', 'Registra actividad en 60 dias del ano.'),
        (yearly_completed_tasks >= 150, 'Ano productivo', 'Completa 150 tareas este ano.'),
        (yearly_effective_minutes >= 6000, 'Ano de enfoque', 'Acumula 100 horas de enfoque este ano.'),
        (
            yearly_completed_tasks >= 300 and yearly_effective_minutes >= 12000,
            'Maestria anual',
            'Completa 300 tareas y 200 horas de enfoque en el ano.',
        ),
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



def period_task_queryset(user, start_date, end_date):
    return Task.objects.filter(owner=user).filter(
        Q(created_at__date__range=(start_date, end_date))
        | Q(updated_at__date__range=(start_date, end_date))
        | Q(due_date__range=(start_date, end_date))
    ).distinct()


def build_focus_series(sessions, view, start_date, end_date):
    completed_sessions = sessions.filter(status=SessionStatus.COMPLETED)
    if view == 'day':
        buckets = [
            {
                'key': f'{hour:02d}',
                'label': f'{hour:02d}:00-{hour + 4:02d}:00',
                'short_label': f'{hour:02d}h',
                'minutes': 0,
            }
            for hour in range(0, 24, 4)
        ]
        bucket_by_hour = {int(bucket['key']): bucket for bucket in buckets}
        for session in completed_sessions:
            local_start = timezone.localtime(session.start_at)
            bucket_hour = (local_start.hour // 4) * 4
            bucket_by_hour[bucket_hour]['minutes'] += session.effective_time
        return buckets

    if view == 'week':
        weekdays = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        buckets = []
        for offset in range(7):
            current_date = start_date + timedelta(days=offset)
            buckets.append({
                'key': current_date.isoformat(),
                'label': weekdays[offset],
                'short_label': weekdays[offset][:3],
                'minutes': 0,
            })
    else:
        buckets = []
        _, days_in_month = monthrange(start_date.year, start_date.month)
        for day in range(1, days_in_month + 1):
            current_date = start_date.replace(day=day)
            buckets.append({
                'key': current_date.isoformat(),
                'label': f'{day}/{current_date.month}',
                'short_label': str(day),
                'minutes': 0,
            })

    bucket_by_date = {bucket['key']: bucket for bucket in buckets}
    for session in completed_sessions:
        local_date = timezone.localtime(session.start_at).date().isoformat()
        if local_date in bucket_by_date:
            bucket_by_date[local_date]['minutes'] += session.effective_time
    return buckets


def build_technique_distribution(sessions):
    technique_labels = {
        ProductivityTechnique.POMODORO: 'Pomodoro',
        ProductivityTechnique.TIME_BLOCKING: 'Time Blocking',
        ProductivityTechnique.FIFTY_TWO_SEVENTEEN: '52/17',
    }
    totals = {technique: 0 for technique in technique_labels}
    for row in sessions.filter(status=SessionStatus.COMPLETED).values('technique').annotate(
        total=Sum('effective_time')
    ):
        totals[row['technique']] = row['total'] or 0

    total_minutes = sum(totals.values())
    distribution = []
    for technique, label in technique_labels.items():
        minutes = totals[technique]
        distribution.append({
            'technique': technique,
            'label': label,
            'minutes': minutes,
            'percentage': round((minutes / total_minutes * 100) if total_minutes else 0),
        })
    return distribution


def consecutive_productivity_days(user, until_date):
    session_dates = set(
        ProductivitySession.objects.filter(
            user=user,
            status=SessionStatus.COMPLETED,
            start_at__date__lte=until_date,
        ).values_list('start_at__date', flat=True)
    )
    cursor = until_date
    streak = 0
    while cursor in session_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


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

    def list(self, request, *args, **kwargs):
        assign_productivity_achievements(request.user)
        return super().list(request, *args, **kwargs)

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
        view, start_date, end_date, error = parse_period(request)
        if error:
            return error

        user = request.user
        selected_date = parse_date(request.query_params.get('date', '')) or timezone.localdate()
        all_tasks = Task.objects.filter(owner=user)
        period_tasks = period_task_queryset(user, start_date, end_date)
        period_sessions = ProductivitySession.objects.filter(
            user=user,
            start_at__date__range=(start_date, end_date),
        )
        period_projects = Project.objects.filter(owner=user).filter(
            Q(created_at__date__lte=end_date) & (Q(end_date__isnull=True) | Q(end_date__gte=start_date))
        ).distinct()

        tasks_created = all_tasks.filter(created_at__date__range=(start_date, end_date)).count()
        tasks_completed = all_tasks.filter(
            status=TaskStatus.COMPLETED,
            updated_at__date__range=(start_date, end_date),
        ).count()
        registered_time = period_sessions.aggregate(total=Sum('total_duration'))['total'] or 0
        effective_minutes = period_sessions.aggregate(total=Sum('effective_time'))['total'] or 0
        break_minutes = max(registered_time - effective_minutes, 0)
        useful_tasks = period_tasks.exclude(status=TaskStatus.CANCELLED).count()
        if registered_time:
            progress = effective_minutes / registered_time * 100
        elif useful_tasks:
            progress = tasks_completed / useful_tasks * 100
        else:
            progress = 0

        metric = Metric.objects.create(
            user=user,
            tasks_created=tasks_created,
            tasks_completed=tasks_completed,
            registered_time=registered_time,
            effective_minutes=effective_minutes,
            progress_percentage=round(progress, 2),
        )

        tasks_by_status = {
            row['status']: row['total']
            for row in period_tasks.values('status').annotate(total=Count('id')).order_by('status')
        }
        tasks_by_priority = {
            row['priority']: row['total']
            for row in period_tasks.values('priority').annotate(total=Count('id')).order_by('priority')
        }
        technique_distribution = build_technique_distribution(period_sessions)
        sessions_by_technique = {
            item['technique']: item['minutes']
            for item in technique_distribution
        }
        project_progress = []
        for project in period_projects:
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
            'period': {
                'view': view,
                'selected_date': selected_date.isoformat(),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            },
            'summary': {
                'tasks_created': tasks_created,
                'tasks_completed': tasks_completed,
                'active_projects': period_projects.count(),
                'completed_sessions': period_sessions.filter(status=SessionStatus.COMPLETED).count(),
                'registered_time': registered_time,
                'effective_minutes': effective_minutes,
                'break_minutes': break_minutes,
                'productivity_percentage': round(progress),
                'consecutive_days': consecutive_productivity_days(user, selected_date),
            },
            'metric': MetricSerializer(metric).data,
            'tasks_by_status': tasks_by_status,
            'tasks_by_priority': tasks_by_priority,
            'sessions_by_technique': sessions_by_technique,
            'technique_distribution': technique_distribution,
            'focus_series': build_focus_series(period_sessions, view, start_date, end_date),
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
