from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "xp", "study_streak")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Flemy", {"fields": ("role", "photo", "xp", "study_streak", "last_study_date")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Flemy", {"fields": ("email", "role")}),
    )
