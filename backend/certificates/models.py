import uuid

from django.conf import settings
from django.db import models

from courses.models import Course


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="certificates", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="certificates", on_delete=models.PROTECT)
    code = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "certificado"
        verbose_name_plural = "certificados"

    def __str__(self) -> str:
        return f"{self.code} - {self.user.email}"
