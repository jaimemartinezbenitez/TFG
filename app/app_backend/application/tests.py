# Autor: Jaime Martínez Benítez
# TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
# Archivo: "tests.py"
# Descripcion: Contiene pruebas del backend.

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Achievement,
    CollaborationStatus,
    Export,
    Notification,
    PasswordResetToken,
    ProductivitySession,
    ProductivityTechnique,
    Project,
    ResourceType,
    SessionStatus,
    Task,
    TaskStatus,
    UserProfile,
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
        notification = Notification.objects.create(user=user, task=task, message="Aviso")

        self.assertEqual(str(project), "TFG")
        self.assertEqual(str(task), "Escribir memoria")
        self.assertIn("owner", str(session))
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
