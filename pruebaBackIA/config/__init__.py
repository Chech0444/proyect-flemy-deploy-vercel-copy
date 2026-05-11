# config/__init__.py
# Importar la app de Celery al inicio de Django
from .celery import app as celery_app

__all__ = ('celery_app',)
