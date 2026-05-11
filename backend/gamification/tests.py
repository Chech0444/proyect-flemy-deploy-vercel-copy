from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from gamification.models import XPTransaction

User = get_user_model()


class GamificationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="studentpass123",
            xp=120,
            study_streak=3,
        )
        XPTransaction.objects.create(user=self.user, amount=20, reason="Leccion completada")
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "studentpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_dashboard_returns_level(self):
        response = self.client.get("/api/v1/gamification/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["level"], 2)

    def test_leaderboard_returns_users(self):
        response = self.client.get("/api/v1/gamification/leaderboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
