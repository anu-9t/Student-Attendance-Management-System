from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Django auth user plus the role used for access control (SAD Figure 4.1)."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
