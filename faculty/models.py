from django.conf import settings
from django.db import models


class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "faculty"

    def __str__(self):
        return f"{self.employee_id} {self.name}"
