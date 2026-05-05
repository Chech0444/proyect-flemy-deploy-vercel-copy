from django.contrib import admin

from certificates.models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "code", "generated_at")
