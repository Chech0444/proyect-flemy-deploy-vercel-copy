from django.conf import settings
from django.db import models


class XPTransaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="xp_transactions", on_delete=models.CASCADE
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.email} {self.amount}"

    class Meta:
        verbose_name = "transaccion de XP"
        verbose_name_plural = "transacciones de XP"
