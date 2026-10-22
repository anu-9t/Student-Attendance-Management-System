from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render

from accounts.models import User
from faculty.models import Faculty
from subjects.models import SubjectAssignment


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
