from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, default="Development")
    level = models.CharField(max_length=50, choices=[('Básico', 'Básico'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')], default='Básico')
    duration_hours = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "curso"
        verbose_name_plural = "cursos"


class Section(models.Model):
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")
        verbose_name = "seccion"
        verbose_name_plural = "secciones"

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(Section, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    video_url = models.URLField()
    is_premium = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("section", "order")
        verbose_name = "leccion"
        verbose_name_plural = "lecciones"

    def __str__(self) -> str:
        return self.title


# ===================================================
# Modelos de Procesamiento de Video con IA
# (Integrados desde pruebaBackIA)
# ===================================================

class Video(models.Model):
    """
    Modelo de Video.
    Almacena el archivo de video subido y se asocia a una lección.
    Al subirse, se dispara el procesamiento automático con IA.
    """
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='video',
        verbose_name='Lección'
    )
    video_file = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        verbose_name='Archivo de video'
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre original'
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Duración (segundos)'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamaño del archivo (bytes)'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de subida'
    )

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Video: {self.original_filename or self.video_file.name}'


class Transcription(models.Model):
    """
    Modelo de Transcripción.
    Almacena la transcripción del audio del video, generada
    automáticamente por Whisper.
    """
    video = models.OneToOneField(
        Video,
        on_delete=models.CASCADE,
        related_name='transcription',
        verbose_name='Video'
    )
    full_text = models.TextField(
        verbose_name='Texto completo'
    )
    segments = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Segmentos con timestamps',
        help_text='Lista de segmentos con timestamps [{start, end, text}]'
    )
    language = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Idioma detectado'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        verbose_name = 'Transcripción'
        verbose_name_plural = 'Transcripciones'

    def __str__(self):
        return f'Transcripción de {self.video}'


class Summary(models.Model):
    """
    Modelo de Resumen.
    Almacena el resumen del contenido del video, generado
    automáticamente por Google Gemini.
    """
    video = models.OneToOneField(
        Video,
        on_delete=models.CASCADE,
        related_name='summary',
        verbose_name='Video'
    )
    content = models.TextField(
        verbose_name='Resumen'
    )
    key_points = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Puntos clave',
        help_text='Lista de los puntos más importantes'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        verbose_name = 'Resumen'
        verbose_name_plural = 'Resúmenes'

    def __str__(self):
        return f'Resumen de {self.video}'


class QuizQuestion(models.Model):
    """
    Modelo de Pregunta de Quiz.
    Almacena preguntas de opción múltiple generadas automáticamente
    por Google Gemini basadas en la transcripción del video.
    """
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='quiz_questions',
        verbose_name='Video'
    )
    question = models.TextField(
        verbose_name='Pregunta'
    )
    options = models.JSONField(
        verbose_name='Opciones',
        help_text='Lista de 4 opciones de respuesta'
    )
    correct_option = models.IntegerField(
        verbose_name='Opción correcta',
        help_text='Índice de la opción correcta (0-3)'
    )
    explanation = models.TextField(
        blank=True,
        verbose_name='Explicación',
        help_text='Explicación de por qué la respuesta es correcta'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        verbose_name = 'Pregunta de Quiz'
        verbose_name_plural = 'Preguntas de Quiz'
        ordering = ['created_at']

    def __str__(self):
        return f'Pregunta: {self.question[:50]}...'


class ProcessingStatus(models.Model):
    """
    Modelo de Estado de Procesamiento.
    Rastrea el estado del pipeline de procesamiento de cada video:
    PENDING → PROCESSING → COMPLETED/ERROR
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PROCESSING = 'processing', 'Procesando'
        COMPLETED = 'completed', 'Completado'
        ERROR = 'error', 'Error'

    class Step(models.TextChoices):
        WAITING = 'waiting', 'En espera'
        EXTRACTING_AUDIO = 'extracting_audio', 'Extrayendo audio'
        TRANSCRIBING = 'transcribing', 'Transcribiendo'
        GENERATING_SUMMARY = 'generating_summary', 'Generando resumen'
        GENERATING_QUIZ = 'generating_quiz', 'Generando preguntas'
        DONE = 'done', 'Finalizado'

    video = models.OneToOneField(
        Video,
        on_delete=models.CASCADE,
        related_name='processing_status',
        verbose_name='Video'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    current_step = models.CharField(
        max_length=30,
        choices=Step.choices,
        default=Step.WAITING,
        verbose_name='Paso actual'
    )
    progress_percent = models.IntegerField(
        default=0,
        verbose_name='Progreso (%)'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error'
    )
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='ID de tarea Celery'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Inicio del procesamiento'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fin del procesamiento'
    )

    class Meta:
        verbose_name = 'Estado de Procesamiento'
        verbose_name_plural = 'Estados de Procesamiento'

    def __str__(self):
        return f'{self.video} - {self.get_status_display()}'
