from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Section
from learning.models import Enrollment, LessonProgress

User = get_user_model()


class LearningApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="studentpass123",
        )
        self.course = Course.objects.create(
            title="Django API",
            short_description="Curso backend",
            description="Curso completo",
            is_published=True,
        )
        self.section = Section.objects.create(course=self.course, title="Base", order=1)
        self.lesson = Lesson.objects.create(
            section=self.section,
            title="Intro",
            content="Contenido inicial",
            video_url="https://example.com/video",
            order=1,
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "studentpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_user_can_enroll(self):
        response = self.client.post(
            "/api/v1/learning/enrollments/",
            {"course": self.course.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_user_can_complete_lesson_and_get_progress(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        complete = self.client.post(f"/api/v1/learning/lessons/{self.lesson.id}/complete/")
        summary = self.client.get("/api/v1/learning/progress/summary/")
        self.assertEqual(complete.status_code, status.HTTP_200_OK)
        self.assertTrue(
            LessonProgress.objects.filter(user=self.user, lesson=self.lesson, completed=True).exists()
        )
        self.assertEqual(summary.status_code, status.HTTP_200_OK)
        self.assertEqual(summary.data[0]["progress_percent"], 100.0)
