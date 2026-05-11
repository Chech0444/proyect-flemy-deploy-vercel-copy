from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole

User = get_user_model()


class CoursesApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=UserRole.ADMIN,
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "admin", "password": "adminpass123"},
            format="json",
        )
        self.admin_token = login.data["access"]

    def test_public_catalog_is_available(self):
        response = self.client.get("/api/v1/courses/catalog/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_course_structure(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        course = self.client.post(
            "/api/v1/courses/admin/courses/",
            {
                "title": "Python Base",
                "short_description": "Curso inicial",
                "description": "Contenido completo",
                "thumbnail": "https://example.com/image.png",
                "is_premium": False,
                "is_published": True,
            },
            format="json",
        )
        self.assertEqual(course.status_code, status.HTTP_201_CREATED)
        section = self.client.post(
            f"/api/v1/courses/admin/courses/{course.data['id']}/sections/",
            {"title": "Introduccion", "order": 1},
            format="json",
        )
        self.assertEqual(section.status_code, status.HTTP_201_CREATED)
        lesson = self.client.post(
            f"/api/v1/courses/admin/sections/{section.data['id']}/lessons/",
            {
                "title": "Primer video",
                "content": "Aprender bases",
                "video_url": "https://example.com/video",
                "is_premium": False,
                "order": 1,
                "duration_minutes": 10,
            },
            format="json",
        )
        self.assertEqual(lesson.status_code, status.HTTP_201_CREATED)
