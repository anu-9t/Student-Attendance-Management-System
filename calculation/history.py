"""Attendance history, newest first (SAM-F-016, UC-07)."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.models import User
from accounts.ownership import get_visible_student, student_profile
from accounts.permissions import role_required
from attendance.models import Attendance
from subjects.models import Subject

PER_PAGE = 25


def history_rows(student, subject_id=None):
    rows = (
        Attendance.objects.filter(student=student)
        .select_related("subject", "time_slot")
        .order_by("-date", "-time_slot__start_time")
    )
    if subject_id:
        rows = rows.filter(subject_id=subject_id)
    return rows


def _render(request, student, own):
    subject_id = request.GET.get("subject", "")
    subject_id = int(subject_id) if subject_id.isdigit() else None
    page = Paginator(history_rows(student, subject_id), PER_PAGE).get_page(request.GET.get("page"))
    subjects = Subject.objects.filter(attendance__student=student).distinct()
    return render(
        request,
        "calculation/history.html",
        {"student": student, "rows": page, "page": page, "own": own, "subjects": subjects, "subject_id": subject_id},
    )


@role_required(User.Role.STUDENT)
def my_history(request):
    student = student_profile(request.user)
    if student is None:
        return render(request, "calculation/history.html", {"student": None, "own": True})
    return _render(request, student, own=True)


@login_required
def student_history(request, pk):
    """Faculty (for the classes they teach) and the admin open a student's history (SAM-SEC-004)."""
    student = get_visible_student(request.user, pk)
    return _render(request, student, own=student.user_id == request.user.pk)
