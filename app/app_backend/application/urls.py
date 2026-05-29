from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountDeleteView,
    AchievementViewSet,
    ChangePasswordView,
    CollaborationViewSet,
    ExportViewSet,
    LogoutView,
    MetricViewSet,
    NotificationViewSet,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProductivitySessionViewSet,
    ProfileView,
    ProjectViewSet,
    RegisterView,
    StatisticViewSet,
    TaskViewSet,
    UserListView,
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
    path('users/', UserListView.as_view(), name='user-list'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/delete-account/', AccountDeleteView.as_view(), name='delete-account'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('calendar/', calendar_view, name='calendar'),
]
