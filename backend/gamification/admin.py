from django.contrib import admin

from gamification.models import XPTransaction


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "created_at")
