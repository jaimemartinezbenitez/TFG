from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from rest_framework import serializers

from .models import (
    Achievement,
    Collaboration,
    Export,
    Metric,
    Notification,
    ProductivitySession,
    Project,
    ResourceType,
    Statistic,
    Task,
    TaskStatus,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id', 'role', 'is_active']

    def get_role(self, obj):
        return getattr(getattr(obj, 'profile', None), 'role', 'STANDARD')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=12, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'owner', 'name', 'description', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'owner',
            'project',
            'title',
            'description',
            'priority',
            'status',
            'due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_project(self, project):
        request = self.context.get('request')
        if project and request and project.owner != request.user:
            can_edit = Collaboration.objects.filter(
                user=request.user,
                project=project,
                role__in=['EDITOR', 'ADMIN'],
            ).exists()
            if not can_edit:
                raise serializers.ValidationError('No tienes permisos sobre este proyecto.')
        return project


class CollaborationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Collaboration
        fields = ['id', 'user', 'owner', 'resource_type', 'task', 'project', 'role', 'assigned_at']
        read_only_fields = ['id', 'owner', 'assigned_at']

    def validate(self, attrs):
        resource_type = attrs.get('resource_type')
        task = attrs.get('task')
        project = attrs.get('project')
        request = self.context.get('request')

        if resource_type == ResourceType.TASK and not task:
            raise serializers.ValidationError('Debes indicar una tarea.')
        if resource_type == ResourceType.PROJECT and not project:
            raise serializers.ValidationError('Debes indicar un proyecto.')
        if resource_type == ResourceType.TASK and project:
            raise serializers.ValidationError('Una colaboracion de tarea no puede incluir proyecto.')
        if resource_type == ResourceType.PROJECT and task:
            raise serializers.ValidationError('Una colaboracion de proyecto no puede incluir tarea.')
        if request:
            resource_owner = task.owner if task else project.owner
            if resource_owner != request.user:
                raise serializers.ValidationError('Solo el propietario puede compartir este recurso.')
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'task', 'message', 'event_date', 'read']
        read_only_fields = ['id', 'event_date']


class ProductivitySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivitySession
        fields = [
            'id',
            'technique',
            'status',
            'start_at',
            'end_at',
            'total_duration',
            'effective_time',
            'completed_cycles',
            'configuration',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        start_at = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end_at = attrs.get('end_at', getattr(self.instance, 'end_at', None))
        if start_at and end_at and end_at < start_at:
            raise serializers.ValidationError('La fecha de fin no puede ser anterior al inicio.')
        return attrs


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'achieved_at']
        read_only_fields = ['id', 'achieved_at']


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = [
            'id',
            'tasks_created',
            'tasks_completed',
            'registered_time',
            'effective_minutes',
            'progress_percentage',
            'calculated_at',
        ]
        read_only_fields = ['id', 'calculated_at']


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = ['id', 'metric', 'chart_type', 'visual_data', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = ['id', 'format', 'date_range', 'file', 'generated_at']
        read_only_fields = ['id', 'file', 'generated_at']


class CalendarItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    date = serializers.DateField()
    status = serializers.CharField(required=False)
    priority = serializers.CharField(required=False)


def build_metric_for_user(user):
    tasks = Task.objects.filter(owner=user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status=TaskStatus.COMPLETED).count()
    registered_time = ProductivitySession.objects.filter(user=user).aggregate(
        total=Sum('total_duration')
    )['total'] or 0
    effective_minutes = ProductivitySession.objects.filter(user=user).aggregate(
        total=Sum('effective_time')
    )['total'] or 0
    progress = (completed_tasks / total_tasks * 100) if total_tasks else 0
    return Metric.objects.create(
        user=user,
        tasks_created=total_tasks,
        tasks_completed=completed_tasks,
        registered_time=registered_time,
        effective_minutes=effective_minutes,
        progress_percentage=round(progress, 2),
    )
