from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Section
from users.models import UserRole

User = get_user_model()


class AIToolsApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=UserRole.ADMIN,
        )
        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="studentpass123",
        )
        course = Course.objects.create(
            title="IA aplicada",
            short_description="Curso IA",
            description="Curso completo",
            is_published=True,
        )
        section = Section.objects.create(course=course, title="Modulo", order=1)
        self.lesson = Lesson.objects.create(
            section=section,
            title="Prompting",
            content="Aprende a estructurar prompts efectivos",
            video_url="https://example.com/video",
            order=1,
        )

    def test_authenticated_user_can_get_transcription_and_feedback(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "studentpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        transcription = self.client.post(
            "/api/v1/ai/transcriptions/",
            {"lesson": self.lesson.id},
            format="json",
        )
        feedback = self.client.post(
            "/api/v1/ai/code-feedback/",
            {"lesson_id": self.lesson.id, "language": "python", "code": "print('hola')"},
            format="json",
        )
        chatbot = self.client.post(
            "/api/v1/ai/chatbot/",
            {"lesson_id": self.lesson.id, "question": "¿Qué debo practicar?"},
            format="json",
        )
        self.assertEqual(transcription.status_code, status.HTTP_200_OK)
        self.assertEqual(feedback.status_code, status.HTTP_200_OK)
        self.assertEqual(chatbot.status_code, status.HTTP_200_OK)

    def test_admin_can_generate_exercises(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "admin", "password": "adminpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.post(
            "/api/v1/ai/exercises/",
            {"lesson": self.lesson.id, "prompt_context": "Refuerzo de conceptos"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 3)
