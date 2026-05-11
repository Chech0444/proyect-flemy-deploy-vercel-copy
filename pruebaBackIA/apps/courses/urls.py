"""
URL Patterns de la App de Cursos.

Define todas las rutas de la API para cursos, lecciones y videos.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets (genera URLs automáticamente)
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')

urlpatterns = [
    # Raíz de la API (información general)
    path('', views.api_root, name='api-root'),

    # URLs generadas por el router (cursos CRUD)
    path('', include(router.urls)),

    # ─────────────────────────────────────────
    # Lecciones
    # ─────────────────────────────────────────
    # Listar/crear lecciones de un curso
    path(
        'courses/<int:course_id>/lessons/',
        views.CourseLessonListCreateView.as_view(),
        name='course-lessons'
    ),
    # Detalle de una lección (con video, resumen, preguntas)
    path(
        'lessons/<int:pk>/',
        views.LessonDetailView.as_view(),
        name='lesson-detail'
    ),

    # ─────────────────────────────────────────
    # Videos
    # ─────────────────────────────────────────
    # Subir video
    path(
        'videos/upload/',
        views.VideoUploadView.as_view(),
        name='video-upload'
    ),
    # Estado del procesamiento
    path(
        'videos/<int:video_id>/status/',
        views.VideoStatusView.as_view(),
        name='video-status'
    ),
    # Transcripción del video
    path(
        'videos/<int:video_id>/transcription/',
        views.VideoTranscriptionView.as_view(),
        name='video-transcription'
    ),
    # Resumen generado por IA
    path(
        'videos/<int:video_id>/summary/',
        views.VideoSummaryView.as_view(),
        name='video-summary'
    ),
    # Preguntas de quiz
    path(
        'videos/<int:video_id>/quiz/',
        views.VideoQuizView.as_view(),
        name='video-quiz'
    ),
]
