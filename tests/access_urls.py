"""Small views used only by test_access_control.py."""
from django.http import HttpResponse
from django.urls import include, path
from django.views import View

from accounts.models import User
from accounts.permissions import RoleRequiredMixin, role_required


@role_required(User.Role.ADMIN)
def admin_only(request):
    return HttpResponse("admin page")


@role_required(User.Role.ADMIN, User.Role.FACULTY)
def staff_only(request):
    return HttpResponse("staff page")


class FacultyOnlyView(RoleRequiredMixin, View):
    allowed_roles = (User.Role.FACULTY,)

    def get(self, request):
        return HttpResponse("faculty page")


urlpatterns = [
    path("", include("sams.urls")),
    path("test/admin-only/", admin_only),
    path("test/staff-only/", staff_only),
    path("test/faculty-only/", FacultyOnlyView.as_view()),
]
