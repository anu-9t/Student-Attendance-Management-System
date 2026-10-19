from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Append-only: no edit or delete path (SAM-SEC-005, SAD 3.4)."""

    class Outcome(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        DENIED = "DENIED", "Denied"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=60, blank=True)
    target_id = models.CharField(max_length=60, blank=True)
    outcome = models.CharField(max_length=7, choices=Outcome.choices)
    detail = models.TextField(blank=True)  # includes the reason for attendance edits
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise PermissionError("Audit entries cannot be edited.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Audit entries cannot be deleted.")
