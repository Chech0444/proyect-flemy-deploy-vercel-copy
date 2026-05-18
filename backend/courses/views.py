import logging

from rest_framework import generics, permissions, filters, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from courses.models import (
    Course, Lesson, Section,
    Video, Transcription, Summary, QuizQuestion, ProcessingStatus
)
from courses.serializers import (
    CourseCatalogSerializer,
    CourseSerializer,
    LessonSerializer,
    SectionSerializer,
    CourseDetailSerializer,
    VideoSerializer,
    VideoDetailSerializer,
    VideoUploadSerializer,
    TranscriptionSerializer,
    SummarySerializer,
    QuizQuestionSerializer,
    ProcessingStatusSerializer,
)
from users.permissions import IsAdminRole, IsPremiumUser
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class CourseCatalogView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True).order_by("-created_at")
    serializer_class = CourseCatalogSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_premium']
    search_fields = ['title', 'short_description', 'description']
    ordering_fields = ['price', 'duration_hours', 'created_at']


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_object(self):
        obj = super().get_object()
        # Si el curso es premium y el usuario no, lanzamos error o limitamos
        if obj.is_premium and not (self.request.user.role in ['ROLE_PREMIUM', 'ROLE_ADMIN']):
            raise PermissionDenied("Este curso es exclusivo para usuarios Premium.")
        return obj


class AdminCourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    permission_classes = [IsAdminRole]


class AdminCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminRole]


class AdminSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs["course_id"])

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs["course_id"])


class AdminSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]


class AdminLessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Lesson.objects.filter(section_id=self.kwargs["section_id"])

    def perform_create(self, serializer):
        serializer.save(section_id=self.kwargs["section_id"])


class AdminLessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminRole]


# ===================================================
# Views de Procesamiento de Video con IA
# ===================================================

class VideoUploadView(APIView):
    """
    POST /api/v1/courses/admin/lessons/<id>/upload-video/
    Sube un video a una lección e inicia el procesamiento con IA.
    Solo admins.
    """
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, lesson_id):
        """Subir un video y lanzar procesamiento automático."""
        # Validar que la lección existe
        lesson = get_object_or_404(Lesson, id=lesson_id)

        # Verificar que no tenga ya un video
        if hasattr(lesson, 'video'):
            return Response({
                'status': 'error',
                'message': f'La lección "{lesson.title}" ya tiene un video asociado'
            }, status=status.HTTP_400_BAD_REQUEST)

        video_file = request.FILES.get('video_file')
        if not video_file:
            return Response({
                'status': 'error',
                'message': 'No se recibió ningún archivo de video'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar archivo
        serializer = VideoUploadSerializer(data={
            'lesson_id': lesson_id,
            'video_file': video_file
        })
        serializer.is_valid(raise_exception=True)

        try:
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

            # Lanzar procesamiento en segundo plano
            from django.db import transaction
            from courses.tasks import process_video_task

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
                    'video': VideoSerializer(video, context={'request': request}).data,
                    'check_status_url': f'/api/v1/courses/videos/{video.id}/status/'
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'Error al subir video: {e}', exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Error al subir el video: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoStatusView(APIView):
    """
    GET /api/v1/courses/videos/<id>/status/
    Estado del procesamiento de un video.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, video_id):
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
    GET /api/v1/courses/videos/<id>/transcription/
    Transcripción de un video.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, video_id):
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
                'message': 'La transcripción aún no está disponible.'
            }, status=status.HTTP_404_NOT_FOUND)


class VideoSummaryView(APIView):
    """
    GET /api/v1/courses/videos/<id>/summary/
    Resumen generado por IA de un video.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, video_id):
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
                'message': 'El resumen aún no está disponible.'
            }, status=status.HTTP_404_NOT_FOUND)


class VideoQuizView(APIView):
    """
    GET /api/v1/courses/videos/<id>/quiz/
    Preguntas de quiz generadas por IA.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        questions = video.quiz_questions.all()

        if not questions.exists():
            return Response({
                'status': 'error',
                'message': 'Las preguntas del quiz aún no están disponibles.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizQuestionSerializer(questions, many=True)
        return Response({
            'status': 'success',
            'count': questions.count(),
            'data': serializer.data
        })


class LessonVideoDetailView(APIView):
    """
    GET /api/v1/courses/lessons/<id>/video/
    Obtener toda la información de video de una lección (video, transcripción, resumen, quiz).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)

        if not hasattr(lesson, 'video'):
            return Response({
                'status': 'success',
                'data': None,
                'message': 'Esta lección no tiene video asociado.'
            })

        video = lesson.video
        serializer = VideoDetailSerializer(video, context={'request': request})
        return Response({
            'status': 'success',
            'data': serializer.data
        })

class VideoRegenerateSummaryView(APIView):
    """
    POST /api/v1/courses/admin/videos/<id>/regenerate-summary/
    Solo admins. Regenera solo el resumen.
    """
    permission_classes = [IsAdminRole]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        if not hasattr(video, 'transcription') or not video.transcription.full_text:
            return Response({
                'status': 'error',
                'message': 'No hay transcripción disponible para generar contenido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from courses.tasks import regenerate_summary_task
        from django.db import transaction
        
        processing_status = video.processing_status
        processing_status.status = ProcessingStatus.Status.PENDING
        processing_status.current_step = ProcessingStatus.Step.WAITING
        processing_status.save()

        def dispatch_task():
            regenerate_summary_task.delay(video.id)
            
        transaction.on_commit(dispatch_task)

        return Response({
            'status': 'success',
            'message': 'Regeneración del resumen iniciada en segundo plano.'
        })

class VideoRegenerateQuizView(APIView):
    """
    POST /api/v1/courses/admin/videos/<id>/regenerate-quiz/
    Solo admins. Regenera solo el quiz.
    """
    permission_classes = [IsAdminRole]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        if not hasattr(video, 'transcription') or not video.transcription.full_text:
            return Response({
                'status': 'error',
                'message': 'No hay transcripción disponible para generar contenido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from courses.tasks import regenerate_quiz_task
        from django.db import transaction
        
        processing_status = video.processing_status
        processing_status.status = ProcessingStatus.Status.PENDING
        processing_status.current_step = ProcessingStatus.Step.WAITING
        processing_status.save()

        def dispatch_task():
            regenerate_quiz_task.delay(video.id)
            
        transaction.on_commit(dispatch_task)

        return Response({
            'status': 'success',
            'message': 'Regeneración del quiz iniciada en segundo plano.'
        })
