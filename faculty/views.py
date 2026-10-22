from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FacultyForm, NewFacultyForm
from .models import Faculty


def _admin_only(request):
    if request.user.role != "ADMIN":
        raise PermissionDenied("Only the administrator manages faculty.")


@login_required
def faculty_list(request):
    _admin_only(request)
    faculty = Faculty.objects.prefetch_related("assignments__subject", "assignments__class_group")
    show_inactive = request.GET.get("show") == "all"
    if not show_inactive:
        faculty = faculty.filter(is_active=True)
    return render(request, "faculty/list.html", {"faculty_members": faculty, "show_inactive": show_inactive})


@login_required
def faculty_add(request):
    """SAM-F-007: add a faculty member with a login."""
    _admin_only(request)
    form = NewFacultyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        member = form.save()
        messages.success(request, f"Added {member.name}.")
        return redirect("faculty:list")
    return render(request, "faculty/form.html", {"form": form, "title": "Add a faculty member"})


@login_required
def faculty_edit(request, pk):
    _admin_only(request)
    member = get_object_or_404(Faculty, pk=pk)
    form = FacultyForm(request.POST or None, instance=member)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Saved changes to {member.name}.")
        return redirect("faculty:list")
    return render(request, "faculty/form.html", {"form": form, "title": f"Edit {member.name}"})


@login_required
def faculty_deactivate(request, pk):
    _admin_only(request)
    member = get_object_or_404(Faculty, pk=pk)
    if request.method == "POST":
        member.is_active = False
        member.save(update_fields=["is_active"])
        if member.user:
            member.user.is_active = False
            member.user.save(update_fields=["is_active"])
        messages.success(request, f"Deactivated {member.name}.")
    return redirect("faculty:list")
