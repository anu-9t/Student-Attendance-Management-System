import datetime as dt

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from accounts.models import User
from accounts.ownership import faculty_assignments, get_visible_student, teaches, visible_students
from accounts.permissions import role_required
from notification.services import get_threshold, is_below
from students.models import ClassGroup
from subjects.models import Subject, SubjectAssignment

from . import export, services

STAFF = (User.Role.ADMIN, User.Role.FACULTY)
PER_PAGE = 50  # rows per page on screen; downloads always have every row


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
    if request.GET.get("format") == "csv":
        return export.as_csv(report)
    if request.GET.get("format") == "pdf":
        return export.as_pdf(report, generated_by=request.user.username)
    date_from, date_to = _dates(request)
    page = Paginator(_flagged_rows(report), PER_PAGE).get_page(request.GET.get("page"))
    return render(
        request,
        "reports/report.html",
        {"report": report, "rows": page, "page": page, "date_from": date_from, "date_to": date_to,
         "threshold": get_threshold()},
    )


def _flagged_rows(report):
    """Each row as ([(cell, below_threshold), ...], student_id), so low percentages can be highlighted."""
    threshold = get_threshold()
    rows = []
    for cells, student_id in zip(report.rows, report.links, strict=True):
        flagged = []
        for i, cell in enumerate(cells):
            low = False
            if i in report.percent_columns and isinstance(cell, str) and cell.endswith("%"):
                low = is_below(float(cell[:-1]), threshold)
            flagged.append((cell, low))
        rows.append((flagged, student_id))
    return rows


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


@role_required(*STAFF)
def student_report(request, pk):
    """SAM-F-018: one student across their subjects (the ones you teach, for faculty)."""
    student = get_visible_student(request.user, pk)
    subjects = services.subjects_for_class(request.user, student.class_group)
    return _show(request, services.student_report(student, subjects, *_dates(request)))


@role_required(*STAFF)
def index(request):
    """Pick a report: the admin sees every class and subject, faculty only their own."""
    if request.user.role == User.Role.ADMIN:
        pairs = SubjectAssignment.objects.select_related("class_group", "subject")
    else:
        pairs = faculty_assignments(request.user)
    pairs = pairs.order_by("class_group__name", "subject__code")
    classes = ClassGroup.objects.filter(pk__in=pairs.values("class_group")).order_by("name")
    query = request.GET.get("q", "").strip()
    students = []
    if query:
        students = visible_students(request.user).filter(Q(srn__icontains=query) | Q(name__icontains=query))[:20]
    return render(
        request,
        "reports/index.html",
        {"pairs": pairs.distinct(), "classes": classes, "query": query, "students": students},
    )
