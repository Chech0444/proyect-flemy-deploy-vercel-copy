from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from certificates.models import Certificate
from courses.models import Course, Lesson, Section
from gamification.models import XPTransaction
from learning.models import Enrollment, LessonProgress
from users.models import UserRole


class Command(BaseCommand):
    help = "Carga datos de ejemplo para el modulo administrativo."

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@flemy.local",
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.set_password("Admin12345!")
        admin.save()

        premium_user, _ = user_model.objects.get_or_create(
            username="premium_user",
            defaults={
                "email": "premium@example.com",
                "first_name": "Paula",
                "last_name": "Premium",
                "role": UserRole.PREMIUM,
                "xp": 240,
                "study_streak": 5,
            },
        )
        premium_user.set_password("Premium123!")
        premium_user.save()

        free_user, _ = user_model.objects.get_or_create(
            username="free_user",
            defaults={
                "email": "free@example.com",
                "first_name": "Felipe",
                "last_name": "Free",
                "role": UserRole.FREE,
                "xp": 60,
                "study_streak": 2,
            },
        )
        free_user.set_password("Free12345!")
        free_user.save()

        python_course, _ = Course.objects.get_or_create(
            slug="python-desde-cero",
            defaults={
                "title": "Python Desde Cero",
                "short_description": "Curso inicial de Python",
                "description": "Variables, control de flujo y funciones.",
                "thumbnail": "https://example.com/python.png",
                "is_premium": False,
                "is_published": True,
            },
        )
        django_course, _ = Course.objects.get_or_create(
            slug="django-rest-avanzado",
            defaults={
                "title": "Django REST Avanzado",
                "short_description": "Backend profesional con Django",
                "description": "Autenticacion, permisos, testing y despliegue.",
                "thumbnail": "https://example.com/django.png",
                "is_premium": True,
                "is_published": True,
            },
        )

        python_section, _ = Section.objects.get_or_create(
            course=python_course,
            order=1,
            defaults={"title": "Fundamentos"},
        )
        django_section, _ = Section.objects.get_or_create(
            course=django_course,
            order=1,
            defaults={"title": "API REST"},
        )

        python_lesson_1, _ = Lesson.objects.get_or_create(
            section=python_section,
            order=1,
            defaults={
                "title": "Variables y tipos",
                "content": "Introduccion a tipos de datos en Python.",
                "video_url": "https://example.com/python-1",
                "is_premium": False,
                "duration_minutes": 12,
            },
        )
        python_lesson_2, _ = Lesson.objects.get_or_create(
            section=python_section,
            order=2,
            defaults={
                "title": "Condicionales",
                "content": "Uso de if, elif y else.",
                "video_url": "https://example.com/python-2",
                "is_premium": False,
                "duration_minutes": 10,
            },
        )
        django_lesson_1, _ = Lesson.objects.get_or_create(
            section=django_section,
            order=1,
            defaults={
                "title": "ViewSets y routers",
                "content": "Construccion de APIs limpias con DRF.",
                "video_url": "https://example.com/django-1",
                "is_premium": True,
                "duration_minutes": 20,
            },
        )

        Enrollment.objects.get_or_create(user=free_user, course=python_course)
        Enrollment.objects.get_or_create(user=premium_user, course=python_course)
        Enrollment.objects.get_or_create(user=premium_user, course=django_course)

        LessonProgress.objects.get_or_create(
            user=free_user,
            lesson=python_lesson_1,
            defaults={"completed": True},
        )
        LessonProgress.objects.get_or_create(
            user=premium_user,
            lesson=python_lesson_1,
            defaults={"completed": True},
        )
        LessonProgress.objects.get_or_create(
            user=premium_user,
            lesson=python_lesson_2,
            defaults={"completed": True},
        )
        LessonProgress.objects.get_or_create(
            user=premium_user,
            lesson=django_lesson_1,
            defaults={"completed": True},
        )

        XPTransaction.objects.get_or_create(
            user=free_user,
            reason="Leccion completada: Variables y tipos",
            defaults={"amount": 20},
        )
        XPTransaction.objects.get_or_create(
            user=premium_user,
            reason="Leccion completada: Condicionales",
            defaults={"amount": 40},
        )

        Certificate.objects.get_or_create(user=premium_user, course=python_course)

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados en el admin."))
