"""Attendance reports (SAM-F-018, SAM-F-019): subject-wise, class-wise and student-wise.

Each builder returns a Report: a title, column headings and rows of plain values. The HTML
page, the CSV download and the PDF all render the same Report, so they always agree.
Counting happens in the database, grouped by student and subject (SAM-NF-001).
"""
from dataclasses import dataclass, field

from django.db.models import Count, Q

from attendance.models import Attendance
from calculation.services import percentage
from students.models import Student
from subjects.models import Subject, SubjectAssignment


@dataclass
class Report:
    title: str
    subtitle: str
    columns: list
    rows: list = field(default_factory=list)
    links: list = field(default_factory=list)  # per row: the student's id, or None
    percent_columns: tuple = ()  # indexes of columns holding a percentage (for highlighting)

    @property
    def slug(self):
        return "".join(c if c.isalnum() else "-" for c in self.title.lower()).strip("-")


def _period(date_from, date_to):
    q = Q()
    if date_from:
        q &= Q(date__gte=date_from)
    if date_to:
        q &= Q(date__lte=date_to)
    return q


def _period_text(date_from, date_to):
    if date_from and date_to:
        return f"{date_from:%d %b %Y} to {date_to:%d %b %Y}"
    if date_from:
        return f"from {date_from:%d %b %Y}"
    if date_to:
        return f"up to {date_to:%d %b %Y}"
    return "all dates"


def _counts(filters):
    """{(student_id, subject_id): (attended, total)} for the matching attendance rows."""
    rows = (
        Attendance.objects.filter(filters)
        .values("student", "subject")
        .annotate(total=Count("id"), attended=Count("id", filter=Q(status=Attendance.Status.PRESENT)))
    )
    return {(r["student"], r["subject"]): (r["attended"], r["total"]) for r in rows}


def _pct_text(attended, total):
    pct = percentage(attended, total)
    return "-" if pct is None else f"{pct}%"


def subject_report(class_group, subject, date_from=None, date_to=None):
    """One subject in one class: each student's attended, held and percentage."""
    students = list(Student.objects.filter(class_group=class_group, is_active=True))
    counts = _counts(Q(subject=subject, student__in=students) & _period(date_from, date_to))
    report = Report(
        title=f"{subject.code} {class_group.name} subject-wise report",
        subtitle=f"{subject.code} {subject.name}, class {class_group.name}, {_period_text(date_from, date_to)}",
        columns=["SRN", "Name", "Attended", "Held", "Percentage"],
        percent_columns=(4,),
    )
    for s in students:
        attended, total = counts.get((s.pk, subject.pk), (0, 0))
        report.rows.append([s.srn, s.name, attended, total, _pct_text(attended, total)])
        report.links.append(s.pk)
    return report


def class_report(class_group, subjects, date_from=None, date_to=None):
    """One class across several subjects: a percentage per student per subject, plus overall."""
    students = list(Student.objects.filter(class_group=class_group, is_active=True))
    subjects = list(subjects)
    counts = _counts(Q(student__in=students, subject__in=subjects) & _period(date_from, date_to))
    report = Report(
        title=f"{class_group.name} class-wise report",
        subtitle=f"Class {class_group.name}, {len(subjects)} subject(s), {_period_text(date_from, date_to)}",
        columns=["SRN", "Name", *[s.code for s in subjects], "Overall"],
        percent_columns=tuple(range(2, 3 + len(subjects))),
    )
    for st in students:
        cells, att_sum, tot_sum = [], 0, 0
        for sub in subjects:
            attended, total = counts.get((st.pk, sub.pk), (0, 0))
            cells.append(_pct_text(attended, total))
            att_sum, tot_sum = att_sum + attended, tot_sum + total
        report.rows.append([st.srn, st.name, *cells, _pct_text(att_sum, tot_sum)])
        report.links.append(st.pk)
    return report


def student_report(student, subjects, date_from=None, date_to=None):
    """One student across the given subjects."""
    subjects = list(subjects)
    counts = _counts(Q(student=student, subject__in=subjects) & _period(date_from, date_to))
    report = Report(
        title=f"{student.srn} student-wise report",
        subtitle=f"{student.name} ({student.srn}), class {student.class_group.name}, {_period_text(date_from, date_to)}",
        columns=["Subject", "Name", "Attended", "Held", "Percentage"],
        percent_columns=(4,),
    )
    att_sum = tot_sum = 0
    for sub in subjects:
        attended, total = counts.get((student.pk, sub.pk), (0, 0))
        report.rows.append([sub.code, sub.name, attended, total, _pct_text(attended, total)])
        report.links.append(None)
        att_sum, tot_sum = att_sum + attended, tot_sum + total
    report.rows.append(["Overall", "", att_sum, tot_sum, _pct_text(att_sum, tot_sum)])
    report.links.append(None)
    return report


def subjects_for_class(user, class_group):
    """Subjects of this class the user may report on: all of them for the admin, own ones for faculty."""
    assignments = SubjectAssignment.objects.filter(class_group=class_group)
    if user.role == "FACULTY":
        assignments = assignments.filter(faculty__user=user)
    return Subject.objects.filter(assignments__in=assignments).distinct()
