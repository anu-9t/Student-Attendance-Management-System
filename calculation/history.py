"""Attendance history, newest first (SAM-F-016, UC-07)."""
from django.shortcuts import render

from accounts.models import User
from accounts.ownership import student_profile
from accounts.permissions import role_required
from attendance.models import Attendance


def history_rows(student):
    return (
        Attendance.objects.filter(student=student)
        .select_related("subject", "time_slot")
        .order_by("-date", "-time_slot__start_time")
    )


@role_required(User.Role.STUDENT)
def my_history(request):
    student = student_profile(request.user)
    rows = history_rows(student) if student else []
    return render(request, "calculation/history.html", {"student": student, "rows": rows, "own": True})
