from rest_framework import serializers

from django.db.models import Sum
from courses.models import (
    Course, Lesson, Section,
    Video, Transcription, Summary, QuizQuestion, ProcessingStatus
)


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "section",
            "title",
            "content",
            "video_url",
            "is_premium",
            "order",
            "duration_minutes",
            "is_completed",
        )
        read_only_fields = ("section",)

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            from learning.models import LessonProgress
            return LessonProgress.objects.filter(user=request.user, lesson=obj, completed=True).exists()
        return False


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ("id", "course", "title", "order", "lessons")
        read_only_fields = ("course",)


class CourseSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "thumbnail",
            "is_premium",
            "is_published",
            "created_at",
            "updated_at",
            "sections",
        )


class CourseCatalogSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()
    total_duration_minutes = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    enrollment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "thumbnail",
            "is_premium",
            "level",
            "created_at",
            "total_duration_minutes",
            "sections_count",
            "progress_percent",
            "is_enrolled",
            "enrollment_count",
        )

    def get_sections_count(self, obj):
        return obj.sections.count()

    def get_progress_percent(self, obj):
        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            from learning.services import compute_course_progress
            return compute_course_progress(request.user, obj)
        return 0

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            from learning.models import Enrollment
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_total_duration_minutes(self, obj):
        total_video = obj.sections.aggregate(
            total=Sum('lessons__video__duration')
        )['total']
        if total_video:
            return int(total_video // 60)
        total_manual = obj.sections.aggregate(
            total=Sum('lessons__duration_minutes')
        )['total']
        return total_manual or 0


class CourseDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    total_duration_minutes = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "thumbnail",
            "is_premium",
            "level",
            "total_duration_minutes",
            "progress_percent",
            "sections",
            "is_enrolled",
        )

    def get_is_enrolled(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        from learning.models import Enrollment
        return Enrollment.objects.filter(user=user, course=obj).exists()

    def get_progress_percent(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return 0
        from learning.services import compute_course_progress
        return compute_course_progress(user, obj)

    def get_total_duration_minutes(self, obj):
        total_video = obj.sections.aggregate(
            total=Sum('lessons__video__duration')
        )['total']
        if total_video:
            return int(total_video // 60)
        total_manual = obj.sections.aggregate(
            total=Sum('lessons__duration_minutes')
        )['total']
        return total_manual or 0


# ===================================================
# Serializers de Procesamiento de Video con IA
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


class VideoSerializer(serializers.ModelSerializer):
    """Serializer básico de video."""
    processing_status = ProcessingStatusSerializer(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'video_file', 'original_filename', 'duration',
            'file_size', 'uploaded_at', 'processing_status'
        ]
        read_only_fields = fields


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
    """Serializer para la subida de videos."""
    lesson_id = serializers.IntegerField(
        help_text='ID de la lección a la que se asocia el video'
    )
    video_file = serializers.FileField(
        help_text='Archivo de video (MP4, AVI, MOV, MKV, WebM)'
    )

    ALLOWED_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'mp3', 'wav']
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

    def validate_video_file(self, value):
        """Validar que el archivo sea un video válido."""
        ext = value.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f'Formato no permitido. Extensiones válidas: '
                f'{", ".join(self.ALLOWED_EXTENSIONS)}'
            )
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

        if hasattr(lesson, 'video'):
            raise serializers.ValidationError(
                f'La lección "{lesson.title}" ya tiene un video asociado'
            )

        return value
