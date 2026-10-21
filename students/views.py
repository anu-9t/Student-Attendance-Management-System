from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import NewStudentForm
from .models import Student


def _admin_only(request):
    if request.user.role != "ADMIN":
        raise PermissionDenied("Only the administrator manages students.")


@login_required
def student_list(request):
    _admin_only(request)
    students = Student.objects.select_related("class_group")
    return render(request, "students/list.html", {"students": students})


@login_required
def student_add(request):
    """SAM-F-004: the administrator adds a student, which also creates their login."""
    _admin_only(request)
    form = NewStudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.save()
        messages.success(request, f"Added {student.name} ({student.srn}).")
        return redirect("students:list")
    return render(request, "students/form.html", {"form": form, "title": "Add a student"})
