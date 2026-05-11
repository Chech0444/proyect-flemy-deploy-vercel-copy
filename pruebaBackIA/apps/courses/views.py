"""
Views (Controladores) de la Plataforma de Cursos Online.

Define los endpoints de la API REST:
- CRUD de cursos
- CRUD de lecciones (anidado bajo cursos)
- Subida de videos con procesamiento automático
- Consulta de resultados de procesamiento (transcripción, resumen, quiz)
- Estado del procesamiento de un video
"""

import logging

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import (
    Course, Lesson, Video, Transcription,
    Summary, QuizQuestion, ProcessingStatus
)
from .serializers import (
    CourseListSerializer, CourseCreateSerializer, CourseDetailSerializer,
    LessonSerializer, LessonCreateSerializer, LessonDetailSerializer,
    VideoSerializer, VideoDetailSerializer, VideoUploadSerializer,
    TranscriptionSerializer, SummarySerializer, QuizQuestionSerializer,
    ProcessingStatusSerializer
)
from .tasks import process_video_task

logger = logging.getLogger(__name__)


# ===================================================
# ViewSet de Cursos
# ===================================================

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cursos.
    
    Endpoints:
    - GET    /api/v1/courses/          → Listar cursos
    - POST   /api/v1/courses/          → Crear curso
    - GET    /api/v1/courses/{id}/     → Detalle del curso
    - PUT    /api/v1/courses/{id}/     → Actualizar curso
    - DELETE /api/v1/courses/{id}/     → Eliminar curso
    """
    queryset = Course.objects.annotate(
        total_lessons=Count('lessons')
    ).all()

    def get_serializer_class(self):
        """Retorna el serializer según la acción."""
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateSerializer
        return CourseDetailSerializer

    def list(self, request, *args, **kwargs):
        """GET /api/v1/courses/ - Listar todos los cursos."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'results': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/courses/{id}/ - Detalle de un curso con sus lecciones."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """POST /api/v1/courses/ - Crear un nuevo curso."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        logger.info(f'Curso creado: {course.title} (ID={course.id})')
        return Response({
            'status': 'success',
            'message': 'Curso creado exitosamente',
            'data': CourseDetailSerializer(course).data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/v1/courses/{id}/ - Eliminar un curso."""
        instance = self.get_object()
        title = instance.title
        instance.delete()
        logger.info(f'Curso eliminado: {title}')
        return Response({
            'status': 'success',
            'message': f'Curso "{title}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)


# ===================================================
# Views de Lecciones
# ===================================================

class CourseLessonListCreateView(generics.ListCreateAPIView):
    """
    Listar y crear lecciones de un curso específico.
    
    Endpoints:
    - GET  /api/v1/courses/{course_id}/lessons/     → Listar lecciones
    - POST /api/v1/courses/{course_id}/lessons/     → Crear lección
    """

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(course_id=course_id).select_related(
            'course'
        ).prefetch_related('video__processing_status')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonCreateSerializer
        return LessonSerializer

    def list(self, request, course_id):
        """GET - Listar lecciones del curso."""
        course = get_object_or_404(Course, id=course_id)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'course': course.title,
            'count': queryset.count(),
            'results': serializer.data
        })

    def create(self, request, course_id):
        """POST - Crear lección en el curso."""
        course = get_object_or_404(Course, id=course_id)
        data = request.data.copy()
        data['course'] = course.id

        serializer = LessonCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        logger.info(f'Lección creada: {lesson.title} en curso {course.title}')

        return Response({
            'status': 'success',
            'message': 'Lección creada exitosamente',
            'data': LessonSerializer(lesson).data
        }, status=status.HTTP_201_CREATED)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detalle, actualización y eliminación de una lección.
    
    Endpoints:
    - GET    /api/v1/lessons/{id}/     → Detalle (con video, resumen, preguntas)
    - PUT    /api/v1/lessons/{id}/     → Actualizar lección
    - DELETE /api/v1/lessons/{id}/     → Eliminar lección
    """
    queryset = Lesson.objects.select_related(
        'course', 'video__transcription', 'video__summary',
        'video__processing_status'
    ).prefetch_related('video__quiz_questions')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LessonCreateSerializer
        return LessonDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """GET - Detalle completo de la lección."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data
        })


# ===================================================
# Views de Video
# ===================================================

class VideoUploadView(APIView):
    """
    Endpoint para subir videos.
    
    POST /api/v1/videos/upload/
    
    Al subir un video:
    1. Valida el archivo
    2. Lo guarda en el servidor
    3. Crea el registro en la base de datos
    4. Inicia automáticamente el procesamiento en segundo plano
    5. Retorna la respuesta inmediatamente (no bloquea)
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Subir un video y lanzar procesamiento automático."""
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesson_id = serializer.validated_data['lesson_id']
        video_file = serializer.validated_data['video_file']

        try:
            # Obtener la lección
            lesson = Lesson.objects.get(id=lesson_id)

            # Crear el registro de video
            video = Video.objects.create(
                lesson=lesson,
                video_file=video_file,
                original_filename=video_file.name,
                file_size=video_file.size
            )

            # Crear estado de procesamiento
            processing_status = ProcessingStatus.objects.create(
                video=video,
                status=ProcessingStatus.Status.PENDING,
                current_step=ProcessingStatus.Step.WAITING
            )

            # Lanzar procesamiento en segundo plano asegurando que el commit ha finalizado
            from django.db import transaction
            
            def dispatch_task():
                task = process_video_task.delay(video.id)
                processing_status.celery_task_id = task.id
                processing_status.save(update_fields=['celery_task_id'])
                logger.info(
                    f'Video subido: {video_file.name} '
                    f'(ID={video.id}, Task={task.id})'
                )
                
            transaction.on_commit(dispatch_task)

            return Response({
                'status': 'success',
                'message': (
                    'Video subido exitosamente. '
                    'El procesamiento ha iniciado en segundo plano.'
                ),
                'data': {
                    'video': VideoSerializer(video).data,
                    'task_id': 'pending_assignment',
                    'check_status_url': f'/api/v1/videos/{video.id}/status/'
                }
            }, status=status.HTTP_201_CREATED)

        except Lesson.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'Lección con ID {lesson_id} no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f'Error al subir video: {e}', exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Error al subir el video: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoStatusView(APIView):
    """
    Estado del procesamiento de un video.
    
    GET /api/v1/videos/{id}/status/
    
    Retorna el estado actual, paso actual y progreso del
    procesamiento del video.
    """

    def get(self, request, video_id):
        """Obtener estado del procesamiento."""
        video = get_object_or_404(Video, id=video_id)

        try:
            processing_status = video.processing_status
            serializer = ProcessingStatusSerializer(processing_status)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except ProcessingStatus.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'No hay información de procesamiento para este video'
            }, status=status.HTTP_404_NOT_FOUND)


class VideoTranscriptionView(APIView):
    """
    Transcripción de un video.
    
    GET /api/v1/videos/{id}/transcription/
    """

    def get(self, request, video_id):
        """Obtener la transcripción del video."""
        video = get_object_or_404(Video, id=video_id)

        try:
            transcription = video.transcription
            serializer = TranscriptionSerializer(transcription)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Transcription.DoesNotExist:
            return Response({
                'status': 'error',
                'message': (
                    'La transcripción aún no está disponible. '
                    'Verifica el estado del procesamiento.'
                )
            }, status=status.HTTP_404_NOT_FOUND)


class VideoSummaryView(APIView):
    """
    Resumen de un video.
    
    GET /api/v1/videos/{id}/summary/
    """

    def get(self, request, video_id):
        """Obtener el resumen generado por IA."""
        video = get_object_or_404(Video, id=video_id)

        try:
            summary = video.summary
            serializer = SummarySerializer(summary)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Summary.DoesNotExist:
            return Response({
                'status': 'error',
                'message': (
                    'El resumen aún no está disponible. '
                    'Verifica el estado del procesamiento.'
                )
            }, status=status.HTTP_404_NOT_FOUND)


class VideoQuizView(APIView):
    """
    Preguntas de quiz de un video.
    
    GET /api/v1/videos/{id}/quiz/
    """

    def get(self, request, video_id):
        """Obtener las preguntas del quiz."""
        video = get_object_or_404(Video, id=video_id)
        questions = video.quiz_questions.all()

        if not questions.exists():
            return Response({
                'status': 'error',
                'message': (
                    'Las preguntas del quiz aún no están disponibles. '
                    'Verifica el estado del procesamiento.'
                )
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizQuestionSerializer(questions, many=True)
        return Response({
            'status': 'success',
            'count': questions.count(),
            'data': serializer.data
        })


# ===================================================
# Vista de información de la API
# ===================================================

@api_view(['GET'])
def api_root(request):
    """
    GET /api/v1/
    
    Retorna información general de la API y los endpoints disponibles.
    """
    return Response({
        'status': 'success',
        'message': '🎓 Plataforma de Cursos Online - API v1',
        'version': '1.0.0',
        'endpoints': {
            'courses': {
                'list': '/api/v1/courses/',
                'create': '/api/v1/courses/',
                'detail': '/api/v1/courses/{id}/',
            },
            'lessons': {
                'list_by_course': '/api/v1/courses/{course_id}/lessons/',
                'create_in_course': '/api/v1/courses/{course_id}/lessons/',
                'detail': '/api/v1/lessons/{id}/',
            },
            'videos': {
                'upload': '/api/v1/videos/upload/',
                'processing_status': '/api/v1/videos/{id}/status/',
                'transcription': '/api/v1/videos/{id}/transcription/',
                'summary': '/api/v1/videos/{id}/summary/',
                'quiz': '/api/v1/videos/{id}/quiz/',
            }
        }
    })
