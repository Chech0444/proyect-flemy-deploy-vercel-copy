"""
Configuración del Panel de Administración de Django.

Registra todos los modelos con configuraciones personalizadas
para facilitar la gestión desde el panel de admin.
"""

from django.contrib import admin
from .models import (
    Course, Lesson, Video, Transcription,
    Summary, QuizQuestion, ProcessingStatus
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Administración de Cursos."""
    list_display = ['title', 'is_published', 'total_lessons', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_published']
    ordering = ['-created_at']


class VideoInline(admin.StackedInline):
    """Inline de Video dentro de Lección."""
    model = Video
    extra = 0
    readonly_fields = ['duration', 'file_size', 'uploaded_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Administración de Lecciones."""
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['course', 'order']
    inlines = [VideoInline]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administración de Videos."""
    list_display = [
        'original_filename', 'lesson', 'duration_display',
        'file_size_display', 'uploaded_at'
    ]
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'lesson__title']
    readonly_fields = ['duration', 'file_size', 'uploaded_at']

    def duration_display(self, obj):
        """Muestra la duración en formato legible."""
        if obj.duration:
            minutes = int(obj.duration // 60)
            seconds = int(obj.duration % 60)
            return f'{minutes}:{seconds:02d}'
        return '-'
    duration_display.short_description = 'Duración'

    def file_size_display(self, obj):
        """Muestra el tamaño en formato legible."""
        if obj.file_size:
            mb = obj.file_size / (1024 * 1024)
            return f'{mb:.1f} MB'
        return '-'
    file_size_display.short_description = 'Tamaño'

    def save_model(self, request, obj, form, change):
        """Sobreescribe el guardado para disparar la tarea de Celery si es nuevo."""
        is_new = obj.pk is None
        
        # Calcular tamaño del archivo si está presente
        if getattr(obj, 'video_file', None) and not obj.file_size:
            obj.file_size = obj.video_file.size
            
        super().save_model(request, obj, form, change)
        
        if is_new:
            from apps.courses.tasks import process_video_task
            from apps.courses.models import ProcessingStatus
            from django.db import transaction
            import logging
            
            # Crear estado de procesamiento inicial
            processing_status = ProcessingStatus.objects.create(
                video=obj,
                status=ProcessingStatus.Status.PENDING,
                current_step=ProcessingStatus.Step.WAITING
            )
            
            def dispatch_task():
                # Disparar tarea en segundo plano de Celery
                task = process_video_task.delay(obj.id)
                
                # Guardar el ID de Celery
                processing_status.celery_task_id = task.id
                processing_status.save(update_fields=['celery_task_id'])
                
                logging.getLogger(__name__).info(
                    f'Video admin subido: {obj.original_filename} '
                    f'(ID={obj.id}, Task={task.id})'
                )
            
            # Ejecutar de forma segura luego del commit en el Admin
            transaction.on_commit(dispatch_task)


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    """Administración de Transcripciones."""
    list_display = ['video', 'language', 'text_preview', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['full_text']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        """Muestra los primeros 100 caracteres."""
        return obj.full_text[:100] + '...' if len(obj.full_text) > 100 else obj.full_text
    text_preview.short_description = 'Preview'


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    """Administración de Resúmenes."""
    list_display = ['video', 'content_preview', 'num_key_points', 'created_at']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Preview'

    def num_key_points(self, obj):
        return len(obj.key_points) if obj.key_points else 0
    num_key_points.short_description = 'Puntos clave'


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Administración de Preguntas de Quiz."""
    list_display = ['question_preview', 'video', 'correct_option', 'created_at']
    list_filter = ['video', 'created_at']
    search_fields = ['question']
    readonly_fields = ['created_at']

    def question_preview(self, obj):
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_preview.short_description = 'Pregunta'


@admin.register(ProcessingStatus)
class ProcessingStatusAdmin(admin.ModelAdmin):
    """Administración de Estados de Procesamiento."""
    list_display = [
        'video', 'status', 'current_step', 'progress_percent',
        'started_at', 'completed_at'
    ]
    list_filter = ['status', 'current_step']
    readonly_fields = [
        'celery_task_id', 'started_at', 'completed_at'
    ]
