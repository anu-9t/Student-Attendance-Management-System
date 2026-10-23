import datetime as dt

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.models import User
from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment, TimeSlot

from .models import Attendance


@login_required
def select_class(request):
    """SAM-F-010: show and validate the class/subject pairs assigned to the faculty user."""
    if request.user.role != User.Role.FACULTY:
        return HttpResponseForbidden("Only faculty members can view assignments.")

    faculty = get_object_or_404(Faculty, user=request.user, is_active=True)
    faculty_assignments = SubjectAssignment.objects.filter(faculty=faculty).select_related(
        "class_group", "subject"
    ).order_by("class_group__name", "subject__code")

    selected_assignment = None
    class_id = request.GET.get("class_id")
    subject_id = request.GET.get("subject_id")
    if class_id is not None or subject_id is not None:
        try:
            if class_id is None or subject_id is None:
                raise ValueError
            selected_assignment = faculty_assignments.get(
                class_group_id=int(class_id), subject_id=int(subject_id)
            )
        except (ValueError, SubjectAssignment.DoesNotExist):
            return HttpResponseNotFound("That class and subject are not assigned to you.")

    return render(
        request,
        "attendance/select.html",
        {
            "assignments": faculty_assignments,
            "selected_assignment": selected_assignment,
        },
    )


def _assignment_for(request, class_id, subject_id):
    """The faculty member's own assignment for this class and subject, or None."""
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    if faculty is None:
        return None, None
    assignment = (
        SubjectAssignment.objects.filter(faculty=faculty, class_group_id=class_id, subject_id=subject_id)
        .select_related("class_group", "subject")
        .first()
    )
    return faculty, assignment


@login_required
def mark(request, class_id, subject_id):
    """SAM-F-011: the marking sheet, one row per active student in the class."""
    if request.user.role != User.Role.FACULTY:
        return HttpResponseForbidden("Only faculty members mark attendance.")
    faculty, assignment = _assignment_for(request, class_id, subject_id)
    if assignment is None:
        return HttpResponseNotFound("That class and subject are not assigned to you.")

    students = Student.objects.filter(class_group=assignment.class_group, is_active=True)
    context = {
        "assignment": assignment,
        "students": students,
        "slots": TimeSlot.objects.all(),
        "today": timezone.localdate(),
        "chosen_date": request.POST.get("date") or timezone.localdate().isoformat(),
        "chosen_slots": [int(x) for x in request.POST.getlist("slots") if x.isdigit()],
        "errors": [],
    }
    return render(request, "attendance/mark.html", context)
