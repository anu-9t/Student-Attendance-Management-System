"""Attendance percentage (SAM-F-015), worked out in the database.

Every one-hour slot counts as one class, so a two-hour lab counts twice (ADR-004).
"""
from dataclasses import dataclass

from django.db.models import Count, Q

from attendance.models import Attendance
from subjects.models import Subject


def percentage(attended, total):
    """Attended classes as a percentage, one decimal place; None when there were no classes."""
    if not total:
        return None
    return round(attended * 100 / total, 1)


@dataclass
class SubjectAttendance:
    subject: Subject
    attended: int
    total: int

    @property
    def percent(self):
        return percentage(self.attended, self.total)


def _counts():
    return {"total": Count("id"), "attended": Count("id", filter=Q(status=Attendance.Status.PRESENT))}


def student_summary(student):
    """One row per subject taught to the student's class, including subjects with no classes yet."""
    counts = {
        row["subject"]: row
        for row in Attendance.objects.filter(student=student).values("subject").annotate(**_counts())
    }
    subjects = Subject.objects.filter(
        Q(assignments__class_group=student.class_group) | Q(pk__in=counts.keys())
    ).distinct()
    return [
        SubjectAttendance(s, counts.get(s.pk, {}).get("attended", 0), counts.get(s.pk, {}).get("total", 0))
        for s in subjects
    ]


def overall(rows):
    """Total over several SubjectAttendance rows."""
    attended = sum(r.attended for r in rows)
    total = sum(r.total for r in rows)
    return {"attended": attended, "total": total, "percent": percentage(attended, total)}


def subject_summary(subject, students):
    """Attended and total for each student in one subject: {student_id: (attended, total)}."""
    rows = (
        Attendance.objects.filter(subject=subject, student__in=students)
        .values("student")
        .annotate(**_counts())
    )
    return {r["student"]: (r["attended"], r["total"]) for r in rows}
