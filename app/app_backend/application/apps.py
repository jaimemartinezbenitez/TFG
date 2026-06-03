# Autor: Jaime Martínez Benítez
# TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
# Archivo: "apps.py"
# Descripcion: Configura la aplicación principal del backend.

from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application'

    def ready(self):
        import application.signals  # noqa: F401
