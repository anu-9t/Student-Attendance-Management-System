from django.conf import settings
from django.db import models


class ClassGroup(models.Model):
    name = models.CharField(max_length=30, unique=True)  # e.g. CSE-3A
    department = models.CharField(max_length=60)
    semester = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name="students")
    srn = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)  # deactivate, never delete (ADR-003)

    def __str__(self):
        return f"{self.srn} {self.name}"
