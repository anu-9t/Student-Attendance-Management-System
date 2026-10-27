import datetime as dt

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from accounts.models import User
from accounts.ownership import teaches
from accounts.permissions import role_required
from students.models import ClassGroup
from subjects.models import Subject

from . import services

STAFF = (User.Role.ADMIN, User.Role.FACULTY)


def _dates(request):
    """date_from / date_to from the query string; anything unreadable is ignored."""
    out = []
    for name in ("date_from", "date_to"):
        try:
            out.append(dt.date.fromisoformat(request.GET.get(name, "")))
        except ValueError:
            out.append(None)
    return out


def _show(request, report):
    date_from, date_to = _dates(request)
    return render(
        request,
        "reports/report.html",
        {"report": report, "rows": zip(report.rows, report.links, strict=True), "date_from": date_from, "date_to": date_to},
    )


@role_required(*STAFF)
def subject_report(request, class_id, subject_id):
    """SAM-F-018: one subject in one class."""
    class_group = get_object_or_404(ClassGroup, pk=class_id)
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.user.role == User.Role.FACULTY and not teaches(request.user, class_group, subject):
        raise PermissionDenied("You don't teach this subject to this class.")
    return _show(request, services.subject_report(class_group, subject, *_dates(request)))


@role_required(*STAFF)
def class_report(request, class_id):
    """SAM-F-019: one class across its subjects (only the ones you teach, for faculty)."""
    class_group = get_object_or_404(ClassGroup, pk=class_id)
    subjects = services.subjects_for_class(request.user, class_group)
    if request.user.role == User.Role.FACULTY and not subjects.exists():
        raise PermissionDenied("You don't teach this class.")
    return _show(request, services.class_report(class_group, subjects, *_dates(request)))
