"""
Configuración de Celery para la Plataforma de Cursos Online.

Este archivo configura Celery para el procesamiento en segundo plano
de videos (transcripción, resumen, generación de preguntas).
"""

import os
from celery import Celery

# Establecer el módulo de settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear la instancia de Celery
app = Celery('courses_platform')

# Leer configuración desde Django settings (prefijo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks en todas las apps instaladas
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug para verificar que Celery funciona."""
    print(f'Request: {self.request!r}')
