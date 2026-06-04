# Autor: Jaime Martínez Benítez
# TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
# Archivo: "test_settings.py"
# Descripcion: Configura el backend para ejecutar pruebas automatizadas.

from .settings import *  # noqa: F401,F403


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
