from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SubjectForm
from .models import Subject


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
