from django.contrib import admin

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
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('role',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('start_date', 'end_date')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'project', 'priority', 'status', 'due_date')
    search_fields = ('title', 'owner__username', 'project__name')
    list_filter = ('priority', 'status', 'due_date')


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('user', 'owner', 'resource_type', 'role', 'assigned_at')
    search_fields = ('user__username', 'owner__username')
    list_filter = ('resource_type', 'role')


admin.site.register(Notification)
admin.site.register(ProductivitySession)
admin.site.register(Achievement)
admin.site.register(Metric)
admin.site.register(Statistic)
admin.site.register(Export)
