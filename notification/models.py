from django.db import models


class SystemSetting(models.Model):
    """Key/value settings. The Notification Module owns attendance_threshold (SAD 3.4)."""

    key = models.CharField(max_length=60, primary_key=True)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.key} = {self.value}"
