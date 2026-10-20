from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def dashboard(request):
    """Display the dashboard for the logged-in user's role."""

    templates = {
        "ADMIN": "dashboards/admin.html",
        "FACULTY": "dashboards/faculty.html",
        "STUDENT": "dashboards/student.html",
    }

    template = templates.get(request.user.role)

    if template is None:
        raise PermissionDenied("Invalid user role.")

    return render(request, template)
