from django.core.exceptions import ValidationError
from django.db import models


class Subject(models.Model):
    """One subject covers both its theory and lab classes (SAD 4.1.1)."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} {self.name}"


class TimeSlot(models.Model):
    """A defined one-hour period, e.g. Period 1, 09:00-10:00."""

    label = models.CharField(max_length=30, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="timeslot_ends_after_it_starts",
            )
        ]

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("A time slot must end after it starts.")

    def __str__(self):
        return f"{self.label} ({self.start_time:%H:%M}-{self.end_time:%H:%M})"


class SubjectAssignment(models.Model):
    faculty = models.ForeignKey("faculty.Faculty", on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    class_group = models.ForeignKey("students.ClassGroup", on_delete=models.CASCADE, related_name="assignments")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["faculty", "subject", "class_group"], name="uniq_faculty_subject_class")
        ]

    def __str__(self):
        return f"{self.faculty} -> {self.subject} ({self.class_group})"
