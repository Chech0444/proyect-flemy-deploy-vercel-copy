from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    FREE = "ROLE_FREE", "Free"
    PREMIUM = "ROLE_PREMIUM", "Premium"
    INSTRUCTOR = "ROLE_INSTRUCTOR", "Instructor"
    ADMIN = "ROLE_ADMIN", "Admin"


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.FREE,
    )
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Breve biografía del usuario.")
    preferences = models.JSONField(default=dict, blank=True, help_text="Preferencias de aprendizaje o configuraciones.")
    xp = models.PositiveIntegerField(default=0)
    study_streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(blank=True, null=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def is_premium(self) -> bool:
        return self.role in {UserRole.PREMIUM, UserRole.ADMIN}

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

class NotificationType(models.TextChoices):
    SUGGESTION = "SUGGESTION", "Sugerencia de IA"
    REMINDER = "REMINDER", "Recordatorio de Curso"
    STREAK = "STREAK", "Hito de Racha"
    SYSTEM = "SYSTEM", "Sistema"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] {self.title} - {self.user.username}"


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    plan_type = models.CharField(max_length=20, default="PREMIUM")
    
    def __str__(self):
        return f"{self.user.email} - {self.plan_type} ({'Activa' if self.is_active else 'Inactiva'})"


# --- Feature: Password Reset via Email Code (from Feature/SantiagoTirado) ---
from django.utils import timezone
from datetime import timedelta

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_valid(self) -> bool:
        # 10 minutes time limit
        return timezone.now() <= self.created_at + timedelta(minutes=10)
        
    def __str__(self):
        return f"Code for {self.user.email} (Valid: {self.is_valid})"
