import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.models import UserRole


class Command(BaseCommand):
    help = "Crea o actualiza un administrador por defecto para el modulo admin."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@flemy.local")
        password = os.getenv("ADMIN_PASSWORD", "Admin12345!")

        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = email
            user.role = UserRole.ADMIN
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        action = "creado" if created else "actualizado"
        self.stdout.write(
            self.style.SUCCESS(
                f"Administrador {action}: username={username} email={email}"
            )
        )
