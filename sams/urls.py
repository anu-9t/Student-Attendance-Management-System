from django.contrib import admin
from django.contrib.auth.decorators import login_not_required
from django.http import JsonResponse
from django.urls import include, path


@login_not_required
def health(request):
    """Used by docker-compose and the pipeline to see that the app is up."""
    return JsonResponse({"status": "ok"})


# Each module keeps its own URLs in <module>/urls.py, so pull requests for
# different modules never need to edit this file.
urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboards.urls")),
    path("students/", include("students.urls")),
    path("faculty/", include("faculty.urls")),
    path("subjects/", include("subjects.urls")),
    path("attendance/", include("attendance.urls")),
    path("notifications/", include("notification.urls")),
    path("reports/", include("reports.urls")),
    path("audit/", include("audit.urls")),
]
