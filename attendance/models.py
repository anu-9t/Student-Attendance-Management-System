from django.db import models


class Attendance(models.Model):
    """One student, one subject, one date, one one-hour time slot (SAD 4.1.1, ADR-004).

    A two-hour lab is stored as two rows, so it counts as two classes.
    """

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"

    student = models.ForeignKey("students.Student", on_delete=models.PROTECT, related_name="attendance")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.PROTECT, related_name="attendance")
    date = models.DateField()
    time_slot = models.ForeignKey("subjects.TimeSlot", on_delete=models.PROTECT, related_name="attendance")
    status = models.CharField(max_length=7, choices=Status.choices)
    marked_by = models.ForeignKey("faculty.Faculty", on_delete=models.PROTECT, related_name="marked_attendance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "subject", "date", "time_slot"], name="uniq_attendance_slot")
        ]
        indexes = [
            models.Index(fields=["student", "subject", "date"], name="att_student_subject_date"),
            models.Index(fields=["subject", "date"], name="att_subject_date"),
        ]

    def __str__(self):
        return f"{self.student.srn} {self.subject.code} {self.date} {self.time_slot.label} {self.status}"
