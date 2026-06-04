# Autor: Jaime Martínez Benítez
# TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
# Archivo: "tests.py"
# Descripcion: Contiene pruebas del backend.

from datetime import timedelta
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, tag
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Achievement,
    Collaboration,
    CollaborationStatus,
    Export,
    Metric,
    Notification,
    PasswordResetToken,
    ProductivitySession,
    ProductivityTechnique,
    Project,
    ResourceType,
    SessionStatus,
    Statistic,
    Task,
    TaskStatus,
    UserProfile,
)
from .permissions import IsOwnerOrReadOnlyCollaborator
from .serializers import (
    CollaborationSerializer,
    LogoutSerializer,
    ProductivitySessionSerializer,
    ProjectSerializer,
    TaskSerializer,
    UserSerializer,
)
from .views import (
    AchievementViewSet,
    CollaborationViewSet,
    ExportViewSet,
    MetricViewSet,
    NotificationViewSet,
    ProductivitySessionViewSet,
    ProjectViewSet,
    StatisticViewSet,
    TaskViewSet,
)

User = get_user_model()


class ApplicationModelTest(TestCase):
    """Pruebas directas sobre modelos y señales principales."""

    @tag("backend")
    def test_user_profile_is_created_with_standard_role(self):
        user = User.objects.create_user(
            username="jaime",
            email="jaime@example.com",
            password="StrongPass1",
        )

        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.role, "STANDARD")
        self.assertIn("jaime", str(user.profile))

    @tag("backend")
    def test_model_string_representations(self):
        user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass1",
        )
        project = Project.objects.create(owner=user, name="TFG")
        task = Task.objects.create(owner=user, project=project, title="Escribir memoria")
        session = ProductivitySession.objects.create(
            user=user,
            technique=ProductivityTechnique.POMODORO,
        )
        achievement = Achievement.objects.create(user=user, name="Logro")
        metric = Metric.objects.create(user=user)
        statistic = Statistic.objects.create(
            user=user,
            metric=metric,
            chart_type="BAR",
        )
        export = Export.objects.create(user=user, format="CSV")
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token="token-modelo",
            expires_at=timezone.now() + timedelta(minutes=30),
        )
        collaboration = Collaboration.objects.create(
            user=User.objects.create_user(
                username="reader",
                email="reader@example.com",
                password="StrongPass1",
            ),
            owner=user,
            resource_type=ResourceType.TASK,
            task=task,
            role="READER",
        )
        notification = Notification.objects.create(user=user, task=task, message="Aviso")

        self.assertEqual(str(project), "TFG")
        self.assertEqual(str(task), "Escribir memoria")
        self.assertIn("owner", str(session))
        self.assertEqual(str(achievement), "Logro")
        self.assertIn("Metricas de", str(metric))
        self.assertIn("BAR", str(statistic))
        self.assertIn("CSV", str(export))
        self.assertIn("Recuperacion password", str(reset_token))
        self.assertIn(ResourceType.TASK, str(collaboration))
        self.assertEqual(str(notification), "Aviso")


class AuthApiTest(APITestCase):
    """Pruebas de registro, perfil, cambio y recuperación de contraseña."""

    def setUp(self):
        self.password = "StrongPass1"
        self.user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password=self.password,
        )

    @tag("backend")
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "password": "StrongPass1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="nuevo")
        self.assertTrue(user.check_password("StrongPass1"))
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    @tag("backend")
    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "otro",
                "email": "usuario@example.com",
                "password": "StrongPass1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @tag("backend")
    def test_login_accepts_email_and_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": self.user.email, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    @tag("backend")
    def test_profile_can_be_updated_and_user_list_excludes_current_user(self):
        other = User.objects.create_user(
            username="compa",
            email="compa@example.com",
            password="StrongPass1",
        )
        self.client.force_authenticate(self.user)

        profile_response = self.client.patch(
            "/api/auth/profile/",
            {
                "first_name": "Jaime",
                "last_name": "Martinez",
                "email": "jaime.actualizado@example.com",
            },
            format="json",
        )

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jaime")
        self.assertEqual(self.user.email, "jaime.actualizado@example.com")

        users_response = self.client.get("/api/users/")
        self.assertEqual(users_response.status_code, status.HTTP_200_OK)
        returned_ids = {item["id"] for item in users_response.data}
        self.assertIn(other.id, returned_ids)
        self.assertNotIn(self.user.id, returned_ids)

    @tag("backend")
    def test_change_password_requires_current_password(self):
        self.client.force_authenticate(self.user)

        wrong_response = self.client.post(
            "/api/auth/change-password/",
            {"old_password": "incorrecta", "password": "NewPass123"},
            format="json",
        )
        self.assertEqual(wrong_response.status_code, status.HTTP_400_BAD_REQUEST)

        ok_response = self.client.post(
            "/api/auth/change-password/",
            {"old_password": self.password, "password": "NewPass123"},
            format="json",
        )

        self.assertEqual(ok_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123"))

    @tag("backend")
    def test_password_reset_generates_token_and_changes_password(self):
        request_response = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json",
        )

        self.assertEqual(request_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", request_response.data)
        self.assertTrue(
            PasswordResetToken.objects.filter(
                user=self.user,
                token=request_response.data["token"],
                used_at__isnull=True,
            ).exists()
        )

        confirm_response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {
                "token": request_response.data["token"],
                "password": "NewPass123",
            },
            format="json",
        )

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123"))
        self.assertFalse(self.user.check_password(self.password))

    @tag("backend")
    def test_password_reset_rejects_unknown_email_and_reused_token(self):
        unknown_response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "nadie@example.com"},
            format="json",
        )
        self.assertEqual(unknown_response.status_code, status.HTTP_400_BAD_REQUEST)

        request_response = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json",
        )
        token = request_response.data["token"]

        first_confirm = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": token, "password": "NewPass123"},
            format="json",
        )
        second_confirm = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": token, "password": "OtherPass1"},
            format="json",
        )

        self.assertEqual(first_confirm.status_code, status.HTTP_200_OK)
        self.assertEqual(second_confirm.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_delete_account_requires_password(self):
        self.client.force_authenticate(self.user)

        wrong_response = self.client.delete(
            "/api/auth/delete-account/",
            {"password": "bad-password"},
            format="json",
        )
        self.assertEqual(wrong_response.status_code, status.HTTP_400_BAD_REQUEST)

        ok_response = self.client.delete(
            "/api/auth/delete-account/",
            {"password": self.password},
            format="json",
        )
        self.assertEqual(ok_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    @tag("backend")
    def test_logout_rejects_invalid_refresh_token(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": "token-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_logout_accepts_valid_refresh_token(self):
        self.client.force_authenticate(self.user)
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskProjectApiTest(APITestCase):
    """Pruebas de tareas, proyectos, colaboración y calendario."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass1",
        )
        self.collaborator = User.objects.create_user(
            username="collaborator",
            email="collaborator@example.com",
            password="StrongPass1",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1",
        )
        self.client.force_authenticate(self.owner)

    @tag("backend")
    def test_create_project_and_task_with_project_assignment(self):
        project_response = self.client.post(
            "/api/projects/",
            {
                "name": "Proyecto TFG",
                "description": "Trabajo final",
                "start_date": "2026-01-01",
                "end_date": "2026-06-30",
            },
            format="json",
        )
        self.assertEqual(project_response.status_code, status.HTTP_201_CREATED)

        task_response = self.client.post(
            "/api/tasks/",
            {
                "title": "Preparar defensa",
                "description": "Ensayar demo",
                "priority": "HIGH",
                "status": "PENDING",
                "due_date": "2026-06-15",
                "project": project_response.data["id"],
            },
            format="json",
        )

        self.assertEqual(task_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(task_response.data["project"], project_response.data["id"])
        self.assertEqual(Task.objects.get(id=task_response.data["id"]).owner, self.owner)

    @tag("backend")
    def test_project_rejects_end_date_before_start_date(self):
        response = self.client.post(
            "/api/projects/",
            {
                "name": "Fechas incorrectas",
                "start_date": "2026-06-30",
                "end_date": "2026-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_user_cannot_assign_task_to_unowned_project_without_permission(self):
        foreign_project = Project.objects.create(owner=self.other, name="Privado")

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Tarea bloqueada",
                "priority": "MEDIUM",
                "status": "PENDING",
                "project": foreign_project.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project", response.data)

    @tag("backend")
    def test_task_complete_action_marks_task_and_creates_achievement(self):
        task = Task.objects.create(owner=self.owner, title="Cerrar capitulo")

        response = self.client.post(f"/api/tasks/{task.id}/complete/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertTrue(
            Achievement.objects.filter(user=self.owner, name="Primeros pasos").exists()
        )
        self.assertIn("new_achievements", response.data)

    @tag("backend")
    def test_task_move_requires_project_and_moves_to_owned_project(self):
        task = Task.objects.create(owner=self.owner, title="Mover tarea")
        project = Project.objects.create(owner=self.owner, name="Destino")

        missing_response = self.client.post(f"/api/tasks/{task.id}/move/", {}, format="json")
        missing_project_response = self.client.post(
            f"/api/tasks/{task.id}/move/",
            {"project": 999999},
            format="json",
        )
        ok_response = self.client.post(
            f"/api/tasks/{task.id}/move/",
            {"project": project.id},
            format="json",
        )

        self.assertEqual(missing_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(missing_project_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ok_response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.project, project)

    @tag("backend")
    def test_create_and_update_completed_tasks_assign_achievements(self):
        create_response = self.client.post(
            "/api/tasks/",
            {
                "title": "Completada al crear",
                "status": TaskStatus.COMPLETED,
            },
            format="json",
        )
        pending_task = Task.objects.create(owner=self.owner, title="Pendiente")
        patch_response = self.client.patch(
            f"/api/tasks/{pending_task.id}/",
            {"status": TaskStatus.COMPLETED},
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Achievement.objects.filter(user=self.owner, name="Primeros pasos").exists()
        )

    @tag("backend")
    def test_collaboration_acceptance_grants_task_access(self):
        task = Task.objects.create(owner=self.owner, title="Tarea compartida")

        invite_response = self.client.post(
            "/api/collaborations/",
            {
                "user_identifier": self.collaborator.email,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "EDITOR",
            },
            format="json",
        )
        self.assertEqual(invite_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(user=self.collaborator).exists())

        self.client.force_authenticate(self.collaborator)
        accept_response = self.client.post(
            f"/api/collaborations/{invite_response.data['id']}/accept/",
            format="json",
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_response.data["status"], CollaborationStatus.ACCEPTED)

        patch_response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"description": "Editada por colaborador"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.description, "Editada por colaborador")

    @tag("backend")
    def test_reader_collaborator_can_read_but_cannot_edit_task(self):
        task = Task.objects.create(owner=self.owner, title="Solo lectura")
        collaboration = Collaboration.objects.create(
            user=self.collaborator,
            owner=self.owner,
            resource_type=ResourceType.TASK,
            task=task,
            role="READER",
            status=CollaborationStatus.ACCEPTED,
        )

        self.client.force_authenticate(self.collaborator)
        detail_response = self.client.get(f"/api/tasks/{task.id}/")
        patch_response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"description": "No permitido"},
            format="json",
        )

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["collaboration_role"], collaboration.role)
        self.assertFalse(detail_response.data["can_edit"])
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("backend")
    def test_project_collaboration_grants_task_access_and_reject_flow(self):
        project = Project.objects.create(owner=self.owner, name="Compartido")
        task = Task.objects.create(owner=self.owner, project=project, title="Dentro")
        invitation = Collaboration.objects.create(
            user=self.collaborator,
            owner=self.owner,
            resource_type=ResourceType.PROJECT,
            project=project,
            role="EDITOR",
        )

        self.client.force_authenticate(self.collaborator)
        reject_response = self.client.post(f"/api/collaborations/{invitation.id}/reject/")
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        self.assertEqual(reject_response.data["status"], CollaborationStatus.REJECTED)

        accepted = Collaboration.objects.create(
            user=self.collaborator,
            owner=self.owner,
            resource_type=ResourceType.PROJECT,
            project=Project.objects.create(owner=self.owner, name="Aceptado"),
            role="EDITOR",
            status=CollaborationStatus.ACCEPTED,
        )
        project_task = Task.objects.create(
            owner=self.owner,
            project=accepted.project,
            title="Visible por proyecto",
        )
        list_response = self.client.get("/api/tasks/")
        patch_response = self.client.patch(
            f"/api/tasks/{project_task.id}/",
            {"description": "Editada desde proyecto"},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIn(project_task.id, {item["id"] for item in list_response.data})
        self.assertNotIn(task.id, {item["id"] for item in list_response.data})
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    @tag("backend")
    def test_collaboration_rejects_self_invitation_duplicate_and_non_owner(self):
        task = Task.objects.create(owner=self.owner, title="Compartir")

        self_response = self.client.post(
            "/api/collaborations/",
            {
                "user_identifier": self.owner.email,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "READER",
            },
            format="json",
        )
        self.assertEqual(self_response.status_code, status.HTTP_400_BAD_REQUEST)

        first_response = self.client.post(
            "/api/collaborations/",
            {
                "user_identifier": self.collaborator.email,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "READER",
            },
            format="json",
        )
        duplicate_response = self.client.post(
            "/api/collaborations/",
            {
                "user_identifier": self.collaborator.email,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "READER",
            },
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(self.other)
        non_owner_response = self.client.post(
            "/api/collaborations/",
            {
                "user_identifier": self.collaborator.email,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "READER",
            },
            format="json",
        )
        self.assertEqual(non_owner_response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_collaboration_filters_and_forbidden_accept_reject(self):
        project = Project.objects.create(owner=self.owner, name="Filtro")
        invitation = Collaboration.objects.create(
            user=self.collaborator,
            owner=self.owner,
            resource_type=ResourceType.PROJECT,
            project=project,
        )

        list_response = self.client.get(
            f"/api/collaborations/?resource_type={ResourceType.PROJECT}&project={project.id}"
        )
        accept_response = self.client.post(
            f"/api/collaborations/{invitation.id}/accept/"
        )
        reject_response = self.client.post(
            f"/api/collaborations/{invitation.id}/reject/"
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in list_response.data], [invitation.id])
        self.assertEqual(accept_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(reject_response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("backend")
    def test_calendar_returns_tasks_and_project_dates(self):
        project = Project.objects.create(
            owner=self.owner,
            name="Calendario",
            start_date=timezone.localdate(),
            end_date=timezone.localdate() + timedelta(days=3),
        )
        task = Task.objects.create(
            owner=self.owner,
            project=project,
            title="Entrega",
            due_date=timezone.localdate(),
            priority="HIGH",
        )

        response = self.client.get(
            f"/api/calendar/?view=month&date={timezone.localdate().isoformat()}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_keys = {(item["type"], item["id"]) for item in response.data["items"]}
        self.assertIn(("task", task.id), item_keys)
        self.assertIn(("project_start", project.id), item_keys)
        self.assertIn(("project_end", project.id), item_keys)

    @tag("backend")
    def test_calendar_rejects_invalid_view(self):
        response = self.client.get("/api/calendar/?view=year")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("view", response.data)


class ProductivityMetricsExportApiTest(APITestCase):
    """Pruebas de productividad, estadísticas, notificaciones y exportación."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="productivo",
            email="productivo@example.com",
            password="StrongPass1",
        )
        self.client.force_authenticate(self.user)

    @tag("backend")
    def test_finish_productivity_session_registers_metrics_and_achievement(self):
        create_response = self.client.post(
            "/api/productivity-sessions/",
            {
                "technique": ProductivityTechnique.POMODORO,
                "status": SessionStatus.IN_PROGRESS,
                "configuration": {
                    "work_minutes": 25,
                    "break_minutes": 5,
                    "cycles": 1,
                },
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        finish_response = self.client.post(
            f"/api/productivity-sessions/{create_response.data['id']}/finish/",
            {
                "status": SessionStatus.COMPLETED,
                "total_duration": 30,
                "effective_time": 25,
                "completed_cycles": 1,
                "configuration": {
                    "work_minutes": 25,
                    "break_minutes": 5,
                    "cycles": 1,
                },
            },
            format="json",
        )

        self.assertEqual(finish_response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_response.data["status"], SessionStatus.COMPLETED)
        self.assertTrue(
            Achievement.objects.filter(
                user=self.user,
                name="Primera sesion productiva",
            ).exists()
        )

    @tag("backend")
    def test_dashboard_returns_summary_and_focus_series(self):
        Task.objects.create(owner=self.user, title="Completada", status=TaskStatus.COMPLETED)
        ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.TIME_BLOCKING,
            status=SessionStatus.COMPLETED,
            total_duration=60,
            effective_time=50,
            completed_cycles=1,
        )

        response = self.client.get("/api/statistics/dashboard/?view=week")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertIn("focus_series", response.data)
        self.assertEqual(response.data["summary"]["registered_time"], 60)
        self.assertEqual(response.data["summary"]["effective_minutes"], 50)

    @tag("backend")
    def test_dashboard_day_and_month_views_cover_focus_buckets(self):
        selected_date = timezone.localdate()
        Project.objects.create(
            owner=self.user,
            name="Proyecto con progreso",
            start_date=selected_date,
        )
        ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.POMODORO,
            status=SessionStatus.COMPLETED,
            total_duration=30,
            effective_time=20,
            completed_cycles=1,
            start_at=timezone.now(),
        )

        day_response = self.client.get(
            f"/api/statistics/dashboard/?view=day&date={selected_date.isoformat()}"
        )
        month_response = self.client.get(
            f"/api/statistics/dashboard/?view=month&date={selected_date.isoformat()}"
        )

        self.assertEqual(day_response.status_code, status.HTTP_200_OK)
        self.assertEqual(month_response.status_code, status.HTTP_200_OK)
        self.assertEqual(day_response.data["focus_series"][0]["short_label"], "00h")
        self.assertGreaterEqual(len(month_response.data["focus_series"]), 28)

    @tag("backend")
    def test_dashboard_uses_task_progress_when_no_registered_time(self):
        Task.objects.create(owner=self.user, title="Hecha", status=TaskStatus.COMPLETED)
        Task.objects.create(owner=self.user, title="Pendiente", status=TaskStatus.PENDING)

        response = self.client.get("/api/statistics/dashboard/?view=week")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["productivity_percentage"], 50)

    @tag("backend")
    def test_dashboard_empty_period_uses_zero_progress(self):
        response = self.client.get("/api/statistics/dashboard/?view=week")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["productivity_percentage"], 0)

    @tag("backend")
    def test_dashboard_rejects_invalid_view(self):
        response = self.client.get("/api/statistics/dashboard/?view=year")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("view", response.data)

    @tag("backend")
    def test_metric_calculate_creates_metric_and_statistic_crud_is_user_scoped(self):
        other = User.objects.create_user(
            username="otroproductivo",
            email="otroproductivo@example.com",
            password="StrongPass1",
        )
        Task.objects.create(owner=self.user, title="Hecha", status=TaskStatus.COMPLETED)
        Task.objects.create(owner=self.user, title="Pendiente", status=TaskStatus.PENDING)
        ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.POMODORO,
            status=SessionStatus.COMPLETED,
            total_duration=30,
            effective_time=25,
            completed_cycles=1,
        )

        metric_response = self.client.post("/api/metrics/calculate/")
        self.assertEqual(metric_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(metric_response.data["tasks_created"], 2)
        self.assertEqual(metric_response.data["tasks_completed"], 1)
        self.assertEqual(metric_response.data["effective_minutes"], 25)

        metric = Metric.objects.get(id=metric_response.data["id"])
        own_statistic_response = self.client.post(
            "/api/statistics/",
            {
                "metric": metric.id,
                "chart_type": "BAR",
                "visual_data": {"label": "Progreso"},
            },
            format="json",
        )
        foreign_metric = Metric.objects.create(user=other, tasks_created=1)
        foreign_statistic = Statistic.objects.create(
            user=other,
            metric=foreign_metric,
            chart_type="PIE",
            visual_data={"label": "Otro"},
        )
        list_response = self.client.get("/api/statistics/")

        self.assertEqual(own_statistic_response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn(foreign_statistic.id, {item["id"] for item in list_response.data})

    @tag("backend")
    def test_metric_list_is_user_scoped(self):
        own_metric = Metric.objects.create(user=self.user, tasks_created=2)
        Metric.objects.create(user=User.objects.create_user(
            username="metricother",
            email="metricother@example.com",
            password="StrongPass1",
        ))

        response = self.client.get("/api/metrics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["id"] for item in response.data}, {own_metric.id})

    @tag("backend")
    def test_productivity_session_validates_technique_configuration(self):
        bad_response = self.client.post(
            "/api/productivity-sessions/",
            {
                "technique": ProductivityTechnique.POMODORO,
                "configuration": {"work_minutes": 25},
            },
            format="json",
        )
        self.assertEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("configuration", bad_response.data)

        time_blocking_response = self.client.post(
            "/api/productivity-sessions/",
            {
                "technique": ProductivityTechnique.TIME_BLOCKING,
                "configuration": {"block_minutes": 90},
            },
            format="json",
        )
        fifty_two_response = self.client.post(
            "/api/productivity-sessions/",
            {
                "technique": ProductivityTechnique.FIFTY_TWO_SEVENTEEN,
                "configuration": {},
            },
            format="json",
        )

        self.assertEqual(time_blocking_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(fifty_two_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(fifty_two_response.data["configuration"]["work_minutes"], 52)
        self.assertEqual(fifty_two_response.data["configuration"]["break_minutes"], 17)

    @tag("backend")
    def test_completed_productivity_session_on_create_assigns_achievement(self):
        response = self.client.post(
            "/api/productivity-sessions/",
            {
                "technique": ProductivityTechnique.TIME_BLOCKING,
                "status": SessionStatus.COMPLETED,
                "total_duration": 60,
                "effective_time": 50,
                "completed_cycles": 1,
                "configuration": {"block_minutes": 60},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Achievement.objects.filter(
                user=self.user,
                name="Primera sesion productiva",
            ).exists()
        )

    @tag("backend")
    def test_finish_productivity_session_rejects_invalid_status_and_negative_values(self):
        productivity_session = ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.TIME_BLOCKING,
            configuration={"block_minutes": 60},
        )

        invalid_status_response = self.client.post(
            f"/api/productivity-sessions/{productivity_session.id}/finish/",
            {"status": SessionStatus.IN_PROGRESS},
            format="json",
        )
        negative_response = self.client.post(
            f"/api/productivity-sessions/{productivity_session.id}/finish/",
            {"status": SessionStatus.COMPLETED, "effective_time": -1},
            format="json",
        )

        self.assertEqual(invalid_status_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(negative_response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_finish_productivity_session_rejects_non_integer_and_bad_config(self):
        productivity_session = ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.TIME_BLOCKING,
            configuration={"block_minutes": 60},
        )

        non_integer_response = self.client.post(
            f"/api/productivity-sessions/{productivity_session.id}/finish/",
            {"total_duration": "abc"},
            format="json",
        )
        bad_config_response = self.client.post(
            f"/api/productivity-sessions/{productivity_session.id}/finish/",
            {"configuration": "no-json"},
            format="json",
        )

        self.assertEqual(non_integer_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(bad_config_response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("backend")
    def test_finish_productivity_session_autocalculates_zero_values(self):
        productivity_session = ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.TIME_BLOCKING,
            start_at=timezone.now() - timedelta(minutes=10),
            configuration={"block_minutes": 60},
        )

        response = self.client.post(
            f"/api/productivity-sessions/{productivity_session.id}/finish/",
            {"status": SessionStatus.COMPLETED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_duration"], 0)
        self.assertEqual(response.data["effective_time"], response.data["total_duration"])

    @tag("backend")
    def test_achievements_endpoint_assigns_task_achievements(self):
        Task.objects.create(owner=self.user, title="Finalizada", status=TaskStatus.COMPLETED)

        response = self.client.get("/api/achievements/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Primeros pasos", {item["name"] for item in response.data})

    @tag("backend")
    def test_notifications_are_generated_and_marked_as_read(self):
        task = Task.objects.create(
            owner=self.user,
            title="Urgente",
            priority="HIGH",
            due_date=timezone.localdate() + timedelta(days=1),
        )

        list_response = self.client.get("/api/notifications/")

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_response.data), 1)
        notification = Notification.objects.get(user=self.user, task=task)
        self.assertFalse(notification.read)

        read_response = self.client.post(f"/api/notifications/{notification.id}/mark_read/")

        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.read)

    @tag("backend")
    def test_generate_reminders_creates_overdue_notification_once(self):
        Task.objects.create(
            owner=self.user,
            title="Vencida",
            priority="LOW",
            due_date=timezone.localdate() - timedelta(days=1),
        )

        first_response = self.client.post("/api/notifications/generate_reminders/")
        second_response = self.client.post("/api/notifications/generate_reminders/")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["created"], 1)
        self.assertIn("esta vencida", first_response.data["notifications"][0]["message"])
        self.assertEqual(second_response.data["created"], 0)

    @tag("backend")
    def test_notifications_are_scoped_to_authenticated_user(self):
        other = User.objects.create_user(
            username="otrouser",
            email="otrouser@example.com",
            password="StrongPass1",
        )
        own_notification = Notification.objects.create(user=self.user, message="Propia")
        Notification.objects.create(user=other, message="Ajena")

        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["id"] for item in response.data}, {own_notification.id})

    @tag("backend")
    def test_notification_can_be_created_by_authenticated_user(self):
        response = self.client.post(
            "/api/notifications/",
            {"message": "Creada desde API"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(user=self.user, message="Creada desde API").exists()
        )

    @tag("backend")
    def test_export_csv_contains_user_metrics_and_project_filtered_tasks(self):
        selected_project = Project.objects.create(owner=self.user, name="Incluido")
        other_project = Project.objects.create(owner=self.user, name="Excluido")
        Task.objects.create(owner=self.user, project=selected_project, title="Dentro")
        Task.objects.create(owner=self.user, project=other_project, title="Fuera")
        ProductivitySession.objects.create(
            user=self.user,
            technique=ProductivityTechnique.POMODORO,
            status=SessionStatus.COMPLETED,
            total_duration=30,
            effective_time=25,
            completed_cycles=1,
        )

        response = self.client.get(f"/api/exports/csv/?project={selected_project.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode("utf-8")
        self.assertIn("Usuario: productivo", content)
        self.assertIn("Email: productivo@example.com", content)
        self.assertIn("Dentro", content)
        self.assertNotIn("Fuera", content)
        self.assertTrue(Export.objects.filter(user=self.user, format="CSV").exists())

    @tag("backend")
    def test_export_pdf_creates_pdf_and_export_records_are_user_scoped(self):
        other = User.objects.create_user(
            username="exportador2",
            email="exportador2@example.com",
            password="StrongPass1",
        )
        Export.objects.create(user=other, format="CSV")

        response = self.client.get("/api/exports/pdf/")
        list_response = self.client.get("/api/exports/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertTrue(Export.objects.filter(user=self.user, format="PDF").exists())
        self.assertTrue(all(item["format"] == "PDF" for item in list_response.data))

    @tag("backend")
    def test_export_rejects_invalid_range_and_foreign_project(self):
        other = User.objects.create_user(
            username="duenoexterno",
            email="duenoexterno@example.com",
            password="StrongPass1",
        )
        foreign_project = Project.objects.create(owner=other, name="Ajeno")

        invalid_range_response = self.client.get(
            "/api/exports/csv/?start=2026-06-30&end=2026-01-01"
        )
        foreign_project_response = self.client.get(
            f"/api/exports/csv/?project={foreign_project.id}"
        )

        self.assertEqual(invalid_range_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("range", invalid_range_response.data)
        self.assertEqual(foreign_project_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("project", foreign_project_response.data)

    @tag("backend")
    def test_export_uses_valid_date_range_and_pdf_returns_errors(self):
        today = timezone.localdate().isoformat()
        Task.objects.create(owner=self.user, title="Exportada con rango")
        csv_response = self.client.get(
            f"/api/exports/csv/?start={today}&end={today}"
        )
        pdf_error_response = self.client.get(
            "/api/exports/pdf/?start=fecha&end=mal"
        )

        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertIn("Exportada con rango", csv_response.content.decode("utf-8"))
        self.assertEqual(pdf_error_response.status_code, status.HTTP_400_BAD_REQUEST)


class BackendBranchCoverageTest(TestCase):
    """Pruebas de ramas internas de serializers, permisos y viewsets."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="branchuser",
            email="branchuser@example.com",
            password="StrongPass1",
        )
        self.other = User.objects.create_user(
            username="branchother",
            email="branchother@example.com",
            password="StrongPass1",
        )
        self.request = SimpleNamespace(user=self.user)

    @tag("backend")
    def test_profile_serializer_rejects_duplicate_username_and_email(self):
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(serializer.validate_username("nuevo-usuario"), "nuevo-usuario")
        with self.assertRaises(Exception):
            serializer.validate_username(self.other.username)

        username_serializer = UserSerializer(
            instance=self.user,
            data={"username": self.other.username, "email": self.user.email},
            partial=True,
        )
        email_serializer = UserSerializer(
            instance=self.user,
            data={"email": self.other.email},
            partial=True,
        )

        self.assertFalse(username_serializer.is_valid())
        self.assertIn("username", username_serializer.errors)
        self.assertFalse(email_serializer.is_valid())
        self.assertIn("email", email_serializer.errors)

    @tag("backend")
    def test_project_serializer_collaboration_fields_for_guest_and_reader(self):
        project = Project.objects.create(owner=self.user, name="Proyecto interno")
        Task.objects.create(owner=self.user, project=project, title="Pendiente")
        Task.objects.create(
            owner=self.user,
            project=project,
            title="Completada",
            status=TaskStatus.COMPLETED,
        )
        anonymous_serializer = ProjectSerializer(
            project,
            context={'request': SimpleNamespace(user=AnonymousUser())},
        )
        self.assertIsNone(anonymous_serializer.data["collaboration_role"])
        self.assertFalse(anonymous_serializer.data["can_edit"])

        Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.PROJECT,
            project=project,
            role="READER",
            status=CollaborationStatus.ACCEPTED,
        )
        reader_serializer = ProjectSerializer(
            project,
            context={'request': SimpleNamespace(user=self.other)},
        )

        self.assertEqual(reader_serializer.data["collaboration_role"], "READER")
        self.assertFalse(reader_serializer.data["can_edit"])
        self.assertEqual(reader_serializer.data["progress_percentage"], 50)

    @tag("backend")
    def test_task_serializer_without_request_and_project_collaboration(self):
        project = Project.objects.create(owner=self.user, name="Proyecto tarea")
        task = Task.objects.create(owner=self.user, project=project, title="Tarea")
        task_without_project = Task.objects.create(owner=self.user, title="Sin proyecto")

        anonymous_serializer = TaskSerializer(
            task,
            context={'request': SimpleNamespace(user=AnonymousUser())},
        )
        no_project_serializer = TaskSerializer(
            task_without_project,
            context={'request': SimpleNamespace(user=self.other)},
        )
        self.assertIsNone(anonymous_serializer.data["collaboration_role"])
        self.assertFalse(anonymous_serializer.data["can_edit"])
        self.assertIsNone(no_project_serializer.data["collaboration_role"])

        Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.PROJECT,
            project=project,
            role="ADMIN",
            status=CollaborationStatus.ACCEPTED,
        )
        collaborator_serializer = TaskSerializer(
            task,
            context={'request': SimpleNamespace(user=self.other)},
        )
        self.assertEqual(collaborator_serializer.data["collaboration_role"], "ADMIN")
        self.assertTrue(collaborator_serializer.data["can_edit"])

    @tag("backend")
    def test_collaboration_serializer_rejects_edge_cases(self):
        task = Task.objects.create(owner=self.user, title="Validaciones")
        project = Project.objects.create(owner=self.user, name="Proyecto")

        cases = [
            (
                {"resource_type": ResourceType.TASK, "task": task.id},
                "user_identifier",
            ),
            (
                {
                    "user_identifier": "desconocido",
                    "resource_type": ResourceType.TASK,
                    "task": task.id,
                },
                "user_identifier",
            ),
            (
                {
                    "user_identifier": self.other.email,
                    "resource_type": ResourceType.TASK,
                    "project": project.id,
                },
                "non_field_errors",
            ),
            (
                {
                    "user_identifier": self.other.email,
                    "resource_type": ResourceType.PROJECT,
                    "task": task.id,
                },
                "non_field_errors",
            ),
            (
                {
                    "user_identifier": self.other.email,
                    "resource_type": ResourceType.TASK,
                },
                "non_field_errors",
            ),
            (
                {
                    "user_identifier": self.other.email,
                    "resource_type": ResourceType.PROJECT,
                },
                "non_field_errors",
            ),
        ]

        for payload, key in cases:
            serializer = CollaborationSerializer(
                data=payload,
                context={'request': self.request},
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn(key, serializer.errors)

        validator = CollaborationSerializer(context={'request': self.request})
        direct_cases = [
            {
                "user": self.other,
                "resource_type": ResourceType.TASK,
                "task": task,
                "project": project,
            },
            {
                "user": self.other,
                "resource_type": ResourceType.PROJECT,
                "task": task,
                "project": project,
            },
        ]
        for attrs in direct_cases:
            with self.assertRaises(Exception):
                validator.validate(attrs)

        project_duplicate = Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.PROJECT,
            project=project,
        )
        duplicate_validator = CollaborationSerializer(context={'request': self.request})
        with self.assertRaises(Exception):
            duplicate_validator.validate({
                "user": project_duplicate.user,
                "resource_type": ResourceType.PROJECT,
                "project": project,
            })

    @tag("backend")
    def test_collaboration_serializer_update_excludes_current_instance(self):
        task = Task.objects.create(owner=self.user, title="Actualizar colaboracion")
        collaboration = Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.TASK,
            task=task,
            role="READER",
        )

        serializer = CollaborationSerializer(
            instance=collaboration,
            data={
                "user": self.other.id,
                "resource_type": ResourceType.TASK,
                "task": task.id,
                "role": "EDITOR",
            },
            context={'request': self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    @tag("backend")
    def test_productivity_serializer_rejects_invalid_dates_and_config(self):
        now = timezone.now()
        invalid_dates = ProductivitySessionSerializer(
            data={
                "technique": ProductivityTechnique.TIME_BLOCKING,
                "start_at": now,
                "end_at": now - timedelta(minutes=5),
                "configuration": {"block_minutes": 30},
            }
        )
        invalid_config = ProductivitySessionSerializer(
            data={
                "technique": ProductivityTechnique.POMODORO,
                "configuration": "no-json",
            }
        )
        optional_cycles = ProductivitySessionSerializer(
            data={
                "technique": ProductivityTechnique.POMODORO,
                "configuration": {
                    "work_minutes": 25,
                    "break_minutes": 5,
                },
            }
        )

        self.assertFalse(invalid_dates.is_valid())
        self.assertFalse(invalid_config.is_valid())
        self.assertTrue(optional_cycles.is_valid(), optional_cycles.errors)

    @tag("backend")
    def test_permissions_without_collaboration_and_non_resource(self):
        permission = IsOwnerOrReadOnlyCollaborator()
        request = SimpleNamespace(user=self.other, method="GET")
        edit_request = SimpleNamespace(user=self.other, method="PATCH")
        task = Task.objects.create(owner=self.user, title="Sin permiso")
        project = Project.objects.create(owner=self.user, name="Proyecto permiso")
        editable_task = Task.objects.create(owner=self.user, title="Con permiso")
        Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.TASK,
            task=editable_task,
            role="EDITOR",
            status=CollaborationStatus.ACCEPTED,
        )
        Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.PROJECT,
            project=project,
            role="READER",
            status=CollaborationStatus.ACCEPTED,
        )

        self.assertFalse(permission.has_object_permission(request, None, task))
        self.assertFalse(permission.has_object_permission(request, None, object()))
        self.assertTrue(permission.has_object_permission(request, None, project))
        self.assertTrue(
            permission.has_object_permission(edit_request, None, editable_task)
        )

    @tag("backend")
    def test_viewset_get_querysets_return_empty_for_anonymous_user(self):
        anonymous_request = SimpleNamespace(
            user=AnonymousUser(),
            method="GET",
            query_params={},
        )
        viewsets = [
            ProjectViewSet,
            TaskViewSet,
            CollaborationViewSet,
            NotificationViewSet,
            ProductivitySessionViewSet,
            AchievementViewSet,
            MetricViewSet,
            StatisticViewSet,
            ExportViewSet,
        ]

        for viewset_class in viewsets:
            viewset = viewset_class()
            viewset.request = anonymous_request
            self.assertFalse(viewset.get_queryset().exists())

    @tag("backend")
    def test_collaboration_queryset_filters_are_applied(self):
        task = Task.objects.create(owner=self.user, title="Filtrable")
        project = Project.objects.create(owner=self.user, name="Filtrable")
        task_collaboration = Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.TASK,
            task=task,
        )
        Collaboration.objects.create(
            user=self.other,
            owner=self.user,
            resource_type=ResourceType.PROJECT,
            project=project,
        )
        viewset = CollaborationViewSet()
        viewset.request = SimpleNamespace(
            user=self.user,
            method="POST",
            query_params={
                "resource_type": ResourceType.TASK,
                "task": str(task.id),
            },
        )

        self.assertEqual(list(viewset.get_queryset()), [task_collaboration])

    @tag("backend")
    def test_authenticated_project_and_metric_querysets_return_user_data(self):
        project = Project.objects.create(owner=self.user, name="Visible")
        metric = Metric.objects.create(user=self.user, tasks_created=1)

        project_viewset = ProjectViewSet()
        project_viewset.request = SimpleNamespace(user=self.user)
        metric_viewset = MetricViewSet()
        metric_viewset.request = SimpleNamespace(user=self.user)

        self.assertEqual(list(project_viewset.get_queryset()), [project])
        self.assertEqual(list(metric_viewset.get_queryset()), [metric])

    @tag("backend")
    def test_serializer_and_viewset_save_helpers(self):
        logout_serializer = LogoutSerializer(data={"refresh": "token-invalido"})
        self.assertTrue(logout_serializer.is_valid())
        with self.assertRaises(Exception):
            logout_serializer.save()

        export_viewset = ExportViewSet()
        export_viewset.request = SimpleNamespace(user=self.user)
        export_viewset.format_kwarg = None
        serializer = export_viewset.get_serializer(data={"format": "CSV"})
        serializer.is_valid(raise_exception=True)
        export_viewset.perform_create(serializer)
        self.assertTrue(Export.objects.filter(user=self.user, format="CSV").exists())
