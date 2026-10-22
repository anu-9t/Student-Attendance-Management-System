from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NewStudentForm, StudentForm
from .models import Student


def _admin_only(request):
    if request.user.role != "ADMIN":
        raise PermissionDenied("Only the administrator manages students.")


@login_required
def student_list(request):
    _admin_only(request)
    students = Student.objects.select_related("class_group")
    query = request.GET.get("q", "").strip()
    if query:
        # SAM-F-006: search by SRN or name
        students = students.filter(Q(srn__icontains=query) | Q(name__icontains=query))
    return render(request, "students/list.html", {"students": students, "query": query})


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


@login_required
def student_edit(request, pk):
    """SAM-F-005: the administrator updates a student's details."""
    _admin_only(request)
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Saved changes to {student.name}.")
        return redirect("students:list")
    return render(request, "students/form.html", {"form": form, "title": f"Edit {student.name}"})
