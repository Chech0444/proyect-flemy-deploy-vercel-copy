"""
Serializers de la Plataforma de Cursos Online.

Define la serialización y validación de datos para la API REST.
Convierte los modelos de Django a/desde JSON y valida la entrada.
"""

from rest_framework import serializers
from .models import (
    Course, Lesson, Video, Transcription,
    Summary, QuizQuestion, ProcessingStatus
)


# ===================================================
# Serializers de base (componentes individuales)
# ===================================================

class ProcessingStatusSerializer(serializers.ModelSerializer):
    """Serializer para el estado del procesamiento del video."""
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    step_display = serializers.CharField(
        source='get_current_step_display', read_only=True
    )

    class Meta:
        model = ProcessingStatus
        fields = [
            'id', 'status', 'status_display', 'current_step',
            'step_display', 'progress_percent', 'error_message',
            'started_at', 'completed_at'
        ]
        read_only_fields = fields


class TranscriptionSerializer(serializers.ModelSerializer):
    """Serializer para la transcripción del video."""
    class Meta:
        model = Transcription
        fields = ['id', 'full_text', 'segments', 'language', 'created_at']
        read_only_fields = fields


class SummarySerializer(serializers.ModelSerializer):
    """Serializer para el resumen generado por IA."""
    class Meta:
        model = Summary
        fields = ['id', 'content', 'key_points', 'created_at']
        read_only_fields = fields


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer para las preguntas del quiz."""
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question', 'options', 'correct_option',
            'explanation', 'created_at'
        ]
        read_only_fields = fields


# ===================================================
# Serializers de Video
# ===================================================

class VideoSerializer(serializers.ModelSerializer):
    """Serializer básico de video."""
    processing_status = ProcessingStatusSerializer(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'video_file', 'original_filename', 'duration',
            'file_size', 'uploaded_at', 'processing_status'
        ]
        read_only_fields = [
            'id', 'original_filename', 'duration', 'file_size',
            'uploaded_at', 'processing_status'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de video con transcripción, resumen y quiz."""
    processing_status = ProcessingStatusSerializer(read_only=True)
    transcription = TranscriptionSerializer(read_only=True)
    summary = SummarySerializer(read_only=True)
    quiz_questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'video_file', 'original_filename', 'duration',
            'file_size', 'uploaded_at', 'processing_status',
            'transcription', 'summary', 'quiz_questions'
        ]
        read_only_fields = fields


class VideoUploadSerializer(serializers.Serializer):
    """
    Serializer para la subida de videos.
    
    Valida el archivo y los datos necesarios para crear
    el video y asociarlo a una lección.
    """
    lesson_id = serializers.IntegerField(
        help_text='ID de la lección a la que se asocia el video'
    )
    video_file = serializers.FileField(
        help_text='Archivo de video (MP4, AVI, MOV, MKV, WebM)'
    )

    # Extensiones de video y audio permitidas
    ALLOWED_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'mp3', 'wav']
    # Tamaño máximo: 500MB
    MAX_FILE_SIZE = 500 * 1024 * 1024

    def validate_video_file(self, value):
        """Validar que el archivo sea un video válido."""
        # Validar extensión
        ext = value.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f'Formato no permitido. Extensiones válidas: '
                f'{", ".join(self.ALLOWED_EXTENSIONS)}'
            )

        # Validar tamaño
        if value.size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f'El archivo es demasiado grande. '
                f'Tamaño máximo: {max_mb:.0f}MB'
            )

        return value

    def validate_lesson_id(self, value):
        """Validar que la lección exista y no tenga video."""
        try:
            lesson = Lesson.objects.get(id=value)
        except Lesson.DoesNotExist:
            raise serializers.ValidationError(
                f'No existe una lección con ID {value}'
            )

        # Verificar que la lección no tenga ya un video
        if hasattr(lesson, 'video'):
            raise serializers.ValidationError(
                f'La lección "{lesson.title}" ya tiene un video asociado'
            )

        return value


# ===================================================
# Serializers de Lección
# ===================================================

class LessonSerializer(serializers.ModelSerializer):
    """Serializer básico de lección (para listados)."""
    has_video = serializers.SerializerMethodField()
    processing_status = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'has_video', 'processing_status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_has_video(self, obj):
        """Retorna True si la lección tiene un video."""
        return hasattr(obj, 'video')

    def get_processing_status(self, obj):
        """Retorna el estado de procesamiento del video."""
        if hasattr(obj, 'video') and hasattr(obj.video, 'processing_status'):
            return obj.video.processing_status.status
        return None


class LessonCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear lecciones."""
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order']
        read_only_fields = ['id']


class LessonDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de lección (con video, resumen, preguntas)."""
    video = VideoDetailSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'video', 'created_at'
        ]
        read_only_fields = fields


# ===================================================
# Serializers de Curso
# ===================================================

class CourseListSerializer(serializers.ModelSerializer):
    """Serializer de curso para listados."""
    total_lessons = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'is_published', 'total_lessons', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_lessons']


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar cursos."""
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'is_published']
        read_only_fields = ['id']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de curso (con lecciones)."""
    lessons = LessonSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail', 'is_published',
            'total_lessons', 'lessons', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
