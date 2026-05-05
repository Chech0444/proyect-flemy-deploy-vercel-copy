from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.URLField(blank=True)
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
