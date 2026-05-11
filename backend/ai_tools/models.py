from django.conf import settings
from django.db import models

from courses.models import Lesson


class TranscriptionJob(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="transcriptions", on_delete=models.CASCADE)
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "transcripcion"
        verbose_name_plural = "transcripciones"


class ExerciseSet(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="exercise_sets", on_delete=models.CASCADE)
    prompt_context = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="exercise_sets", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "set de ejercicios"
        verbose_name_plural = "sets de ejercicios"


class ExerciseQuestion(models.Model):
    exercise_set = models.ForeignKey(
        ExerciseSet, related_name="questions", on_delete=models.CASCADE
    )
    question = models.TextField()
    hint = models.TextField()

    class Meta:
        verbose_name = "pregunta de ejercicio"
        verbose_name_plural = "preguntas de ejercicios"


class CodeFeedbackLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="code_feedback_logs", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(Lesson, related_name="code_feedback_logs", on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    code = models.TextField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "feedback de codigo"
        verbose_name_plural = "feedbacks de codigo"


class ChatbotLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="chatbot_logs", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(Lesson, related_name="chatbot_logs", on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "registro de chatbot"
        verbose_name_plural = "registros de chatbot"
