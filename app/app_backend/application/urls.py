from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AchievementViewSet,
    CollaborationViewSet,
    ExportViewSet,
    MetricViewSet,
    NotificationViewSet,
    ProductivitySessionViewSet,
    ProfileView,
    ProjectViewSet,
    RegisterView,
    StatisticViewSet,
    TaskViewSet,
    calendar_view,
)

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('tasks', TaskViewSet, basename='task')
router.register('collaborations', CollaborationViewSet, basename='collaboration')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('productivity-sessions', ProductivitySessionViewSet, basename='productivity-session')
router.register('achievements', AchievementViewSet, basename='achievement')
router.register('metrics', MetricViewSet, basename='metric')
router.register('statistics', StatisticViewSet, basename='statistic')
router.register('exports', ExportViewSet, basename='export')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('calendar/', calendar_view, name='calendar'),
]
