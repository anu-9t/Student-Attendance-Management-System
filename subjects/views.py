from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignmentForm, SubjectForm, TimeSlotForm
from .models import Subject, SubjectAssignment, TimeSlot


def _admin_only(request):
    if request.user.role != "ADMIN":
        raise PermissionDenied("Only the administrator manages subjects.")


@login_required
def subject_list(request):
    _admin_only(request)
    return render(request, "subjects/subject_list.html", {"subjects": Subject.objects.all()})


@login_required
def subject_add(request):
    """SAM-F-008: create a subject. A subject covers both its theory and lab classes."""
    _admin_only(request)
    form = SubjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        subject = form.save()
        messages.success(request, f"Added {subject.code}.")
        return redirect("subjects:list")
    return render(request, "subjects/form.html", {"form": form, "title": "Add a subject", "back": "subjects:list"})


@login_required
def subject_edit(request, pk):
    _admin_only(request)
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Saved {subject.code}.")
        return redirect("subjects:list")
    return render(request, "subjects/form.html", {"form": form, "title": f"Edit {subject.code}", "back": "subjects:list"})


@login_required
def timeslot_list(request):
    _admin_only(request)
    return render(request, "subjects/timeslot_list.html", {"slots": TimeSlot.objects.all()})


@login_required
def timeslot_add(request):
    """The one-hour periods attendance is marked against (ADR-004)."""
    _admin_only(request)
    form = TimeSlotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        slot = form.save()
        messages.success(request, f"Added {slot.label}.")
        return redirect("subjects:timeslots")
    return render(request, "subjects/form.html", {"form": form, "title": "Add a time slot", "back": "subjects:timeslots"})


@login_required
def timeslot_edit(request, pk):
    _admin_only(request)
    slot = get_object_or_404(TimeSlot, pk=pk)
    form = TimeSlotForm(request.POST or None, instance=slot)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Saved {slot.label}.")
        return redirect("subjects:timeslots")
    return render(request, "subjects/form.html", {"form": form, "title": f"Edit {slot.label}", "back": "subjects:timeslots"})


@login_required
def assignment_list(request):
    """SAM-F-009: which faculty member teaches which subject to which class."""
    _admin_only(request)
    form = AssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        a = form.save()
        messages.success(request, f"{a.faculty.name} now teaches {a.subject.code} to {a.class_group.name}.")
        return redirect("subjects:assignments")
    assignments = SubjectAssignment.objects.select_related("faculty", "subject", "class_group").order_by(
        "faculty__employee_id", "subject__code", "class_group__name"
    )
    return render(request, "subjects/assignments.html", {"assignments": assignments, "form": form})


@login_required
def assignment_remove(request, pk):
    _admin_only(request)
    assignment = get_object_or_404(SubjectAssignment, pk=pk)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment removed.")
    return redirect("subjects:assignments")
