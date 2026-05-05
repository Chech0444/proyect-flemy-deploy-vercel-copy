from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from certificates.models import Certificate
from courses.models import Course, Lesson, Section
from learning.models import Enrollment, LessonProgress

User = get_user_model()


class CertificatesApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="studentpass123",
        )
        self.course = Course.objects.create(
            title="Certificable",
            short_description="Curso final",
            description="Curso completo",
            is_published=True,
        )
        section = Section.objects.create(course=self.course, title="Modulo", order=1)
        lesson = Lesson.objects.create(
            section=section,
            title="Leccion",
            content="Contenido",
            video_url="https://example.com/video",
            order=1,
        )
        Enrollment.objects.create(user=self.user, course=self.course)
        LessonProgress.objects.create(user=self.user, lesson=lesson, completed=True)
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "studentpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_user_can_generate_and_list_certificate(self):
        create_response = self.client.post(f"/api/v1/certificates/courses/{self.course.id}/generate/")
        list_response = self.client.get("/api/v1/certificates/my-certificates/")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertTrue(Certificate.objects.filter(user=self.user, course=self.course).exists())

    def test_user_can_download_certificate(self):
        certificate = Certificate.objects.create(user=self.user, course=self.course)
        response = self.client.get(f"/api/v1/certificates/{certificate.code}/download/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
