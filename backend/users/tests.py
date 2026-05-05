from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole

User = get_user_model()


class UsersApiTests(APITestCase):
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

    def authenticate(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": user.username, "password": "adminpass123" if user == self.admin else "studentpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def test_user_can_register(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "newuser",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "email": "new@example.com",
                "password": "supersegura123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="newuser").role, UserRole.FREE)

    def test_admin_can_list_users(self):
        self.authenticate(self.admin)
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_user_can_update_profile(self):
        self.authenticate(self.user)
        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"first_name": "Ana"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ana")

    def test_user_can_upgrade_to_premium(self):
        self.authenticate(self.user)
        response = self.client.post(
            "/api/v1/users/upgrade-premium/",
            {"role": UserRole.PREMIUM},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, UserRole.PREMIUM)
