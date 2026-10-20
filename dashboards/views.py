from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from faculty.models import Faculty
from students.models import ClassGroup, Student
from subjects.models import Subject

TEMPLATES = {
    "ADMIN": "dashboards/admin.html",
    "FACULTY": "dashboards/faculty.html",
    "STUDENT": "dashboards/student.html",
}


def _context_for(user):
    """Extra details shown on each dashboard."""
    if user.role == "ADMIN":
        return {
            "student_count": Student.objects.filter(is_active=True).count(),
            "faculty_count": Faculty.objects.filter(is_active=True).count(),
            "subject_count": Subject.objects.count(),
            "class_count": ClassGroup.objects.count(),
        }
    if user.role == "FACULTY":
        faculty = Faculty.objects.filter(user=user).first()
        assignments = faculty.assignments.select_related("subject", "class_group") if faculty else []
        return {"faculty": faculty, "assignments": assignments}
    if user.role == "STUDENT":
        return {"student": Student.objects.filter(user=user).select_related("class_group").first()}
    return {}


@login_required
def dashboard(request):
    """Display the dashboard for the logged-in user's role."""
    template = TEMPLATES.get(request.user.role)
    if template is None:
        raise PermissionDenied("Invalid user role.")
    return render(request, template, _context_for(request.user))


def _dashboard_for(role):
    @login_required
    def view(request):
        if request.user.role != role:
            raise PermissionDenied("This dashboard belongs to another role.")
        return render(request, TEMPLATES[role], _context_for(request.user))

    return view


admin_dashboard = _dashboard_for("ADMIN")
faculty_dashboard = _dashboard_for("FACULTY")
student_dashboard = _dashboard_for("STUDENT")
