from django.shortcuts import render

from accounts.models import User
from accounts.permissions import role_required
from students.models import Student

from .services import overall, student_summary


@role_required(User.Role.STUDENT)
def my_percentage(request):
    """SAM-F-015 / UC-03: a student sees their own percentage for each subject."""
    student = Student.objects.filter(user=request.user).select_related("class_group").first()
    rows = student_summary(student) if student else []
    return render(
        request,
        "calculation/my_percentage.html",
        {"student": student, "rows": rows, "overall": overall(rows)},
    )
