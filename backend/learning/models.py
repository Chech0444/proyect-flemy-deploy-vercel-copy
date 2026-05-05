from django.conf import settings
from django.db import models

from courses.models import Course, Lesson


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "inscripcion"
        verbose_name_plural = "inscripciones"

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lesson_progress",
        on_delete=models.CASCADE,
    )
    lesson = models.ForeignKey(Lesson, related_name="progress_records", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "lesson")
        verbose_name = "progreso de leccion"
        verbose_name_plural = "progresos de lecciones"

    def __str__(self) -> str:
        return f"{self.user.email} - {self.lesson.title}"
