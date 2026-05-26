from django.conf import settings
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    STANDARD = 'STANDARD', 'Estandar'
    ADMIN = 'ADMIN', 'Administrador'


class Priority(models.TextChoices):
    LOW = 'LOW', 'Baja'
    MEDIUM = 'MEDIUM', 'Media'
    HIGH = 'HIGH', 'Alta'


class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendiente'
    IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
    COMPLETED = 'COMPLETED', 'Completada'
    CANCELLED = 'CANCELLED', 'Cancelada'


class ResourceType(models.TextChoices):
    TASK = 'TASK', 'Tarea'
    PROJECT = 'PROJECT', 'Proyecto'


class CollaboratorRole(models.TextChoices):
    READER = 'READER', 'Lector'
    EDITOR = 'EDITOR', 'Editor'
    ADMIN = 'ADMIN', 'Administrador'


class ProductivityTechnique(models.TextChoices):
    POMODORO = 'POMODORO', 'Pomodoro'
    TIME_BLOCKING = 'TIME_BLOCKING', 'Time blocking'
    FIFTY_TWO_SEVENTEEN = 'FIFTY_TWO_SEVENTEEN', '52/17'


class SessionStatus(models.TextChoices):
    IN_PROGRESS = 'IN_PROGRESS', 'En curso'
    COMPLETED = 'COMPLETED', 'Completada'
    INTERRUPTED = 'INTERRUPTED', 'Interrumpida'


class ChartType(models.TextChoices):
    BAR = 'BAR', 'Barras'
    PIE = 'PIE', 'Circular'
    LINE = 'LINE', 'Lineal'


class ExportFormat(models.TextChoices):
    CSV = 'CSV', 'CSV'
    PDF = 'PDF', 'PDF'


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STANDARD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
    )
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('owner', 'name')

    def __str__(self):
        return self.name


class Task(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        related_name='tasks',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', 'due_date', '-created_at']

    def __str__(self):
        return self.title


class Collaboration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaborations',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_resources',
    )
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=CollaboratorRole.choices, default=CollaboratorRole.READER)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'task'],
                condition=models.Q(task__isnull=False),
                name='unique_task_collaborator',
            ),
            models.UniqueConstraint(
                fields=['user', 'project'],
                condition=models.Q(project__isnull=False),
                name='unique_project_collaborator',
            ),
        ]
        ordering = ['-assigned_at']

    def clean(self):
        if self.resource_type == ResourceType.TASK:
            self.project = None
            if self.task:
                self.owner = self.task.owner
        if self.resource_type == ResourceType.PROJECT:
            self.task = None
            if self.project:
                self.owner = self.project.owner

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.resource_type} - {self.role}'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    event_date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['read', '-event_date']

    def __str__(self):
        return self.message


class ProductivitySession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='productivity_sessions',
    )
    technique = models.CharField(max_length=30, choices=ProductivityTechnique.choices)
    status = models.CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.IN_PROGRESS)
    start_at = models.DateTimeField(default=timezone.now)
    end_at = models.DateTimeField(null=True, blank=True)
    total_duration = models.PositiveIntegerField(default=0)
    effective_time = models.PositiveIntegerField(default=0)
    completed_cycles = models.PositiveIntegerField(default=0)
    configuration = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-start_at']

    def __str__(self):
        return f'{self.user} - {self.technique}'


class Achievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
    )
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    achieved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-achieved_at']
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Metric(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='metrics',
    )
    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    registered_time = models.PositiveIntegerField(default=0)
    effective_minutes = models.PositiveIntegerField(default=0)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    calculated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-calculated_at']

    def __str__(self):
        return f'Metricas de {self.user} ({self.calculated_at:%Y-%m-%d})'


class Statistic(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='statistics',
    )
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='statistics')
    chart_type = models.CharField(max_length=20, choices=ChartType.choices)
    visual_data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.chart_type} - {self.user}'


class Export(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exports',
    )
    format = models.CharField(max_length=10, choices=ExportFormat.choices)
    date_range = models.CharField(max_length=80, blank=True)
    file = models.FileField(upload_to='exports/', null=True, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.format} - {self.user}'
