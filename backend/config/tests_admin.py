from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from courses.models import Course
from learning.models import Enrollment
from users.models import UserRole

User = get_user_model()

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='admin_test', password='password123')
        
        # Create some data
        Course.objects.create(title="Test Course", short_description="Desc", description="Full desc")
        Enrollment.objects.create(user=self.admin_user, course=Course.objects.first())

    def test_admin_dashboard_metrics(self):
        """Verify that the custom metrics are present in the admin index context."""
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check context
        self.assertIn('course_count', response.context)
        self.assertIn('enrollment_count', response.context)
        self.assertEqual(response.context['course_count'], 1)
        self.assertEqual(response.context['enrollment_count'], 1)
        
        # Check if the custom CSS is linked
        self.assertContains(response, 'flemy-admin.css')
        
        # Check if the metric card for enrollments is rendered
        self.assertContains(response, 'Inscripciones Totales')
