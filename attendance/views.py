import datetime as dt

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment, TimeSlot

from .models import Attendance


@login_required
def select_class(request):
    """SAM-F-010: show and validate the class/subject pairs assigned to the faculty user."""
    if request.user.role != User.Role.FACULTY:
        return HttpResponseForbidden("Only faculty members can view assignments.")

    faculty = get_object_or_404(Faculty, user=request.user, is_active=True)
    faculty_assignments = SubjectAssignment.objects.filter(faculty=faculty).select_related(
        "class_group", "subject"
    ).order_by("class_group__name", "subject__code")

    selected_assignment = None
    class_id = request.GET.get("class_id")
    subject_id = request.GET.get("subject_id")
    if class_id is not None or subject_id is not None:
        try:
            if class_id is None or subject_id is None:
                raise ValueError
            selected_assignment = faculty_assignments.get(
                class_group_id=int(class_id), subject_id=int(subject_id)
            )
        except (ValueError, SubjectAssignment.DoesNotExist):
            return HttpResponseNotFound("That class and subject are not assigned to you.")

    return render(
        request,
        "attendance/select.html",
        {
            "assignments": faculty_assignments,
            "selected_assignment": selected_assignment,
        },
    )


def _assignment_for(request, class_id, subject_id):
    """The faculty member's own assignment for this class and subject, or None."""
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    if faculty is None:
        return None, None
    assignment = (
        SubjectAssignment.objects.filter(faculty=faculty, class_group_id=class_id, subject_id=subject_id)
        .select_related("class_group", "subject")
        .first()
    )
    return faculty, assignment


@login_required
def mark(request, class_id, subject_id):
    """SAM-F-011: the marking sheet, one row per active student in the class."""
    if request.user.role != User.Role.FACULTY:
        return HttpResponseForbidden("Only faculty members mark attendance.")
    faculty, assignment = _assignment_for(request, class_id, subject_id)
    if assignment is None:
        return HttpResponseNotFound("That class and subject are not assigned to you.")

    students = Student.objects.filter(class_group=assignment.class_group, is_active=True)
    context = {
        "assignment": assignment,
        "students": students,
        "slots": TimeSlot.objects.all(),
        "today": timezone.localdate(),
        "chosen_date": request.POST.get("date") or timezone.localdate().isoformat(),
        "chosen_slots": [int(x) for x in request.POST.getlist("slots") if x.isdigit()],
        "errors": [],
    }
    if request.method == "POST":
        errors = _save(request, faculty, assignment, students, context)
        if not errors:
            return redirect("attendance:mark", class_id=class_id, subject_id=subject_id)
        context["errors"] = errors
    return render(request, "attendance/mark.html", context)


def _save(request, faculty, assignment, students, context):
    """SAM-F-012 and SAM-F-013: store the sheet in one transaction, refusing duplicates.

    Returns a list of error messages; an empty list means everything was saved.
    """
    try:
        date = dt.date.fromisoformat(request.POST.get("date", ""))
    except ValueError:
        return ["Please pick a valid date."]
    if date > context["today"]:
        return ["Attendance can't be marked for a future date."]

    slots = list(TimeSlot.objects.filter(pk__in=context["chosen_slots"]))
    if not slots:
        return ["Pick at least one time slot."]

    statuses = {}
    for s in students:
        value = request.POST.get(f"status_{s.pk}")
        if value not in Attendance.Status.values:
            return [f"Mark {s.name} as present or absent."]
        statuses[s] = value

    already = Attendance.objects.filter(
        subject=assignment.subject, date=date, time_slot__in=slots, student__in=students
    ).values_list("time_slot__label", flat=True).distinct()
    if already:
        return [
            f"Attendance for {', '.join(sorted(already))} on {date:%d %b %Y} is already saved. "
            "Nothing was saved this time; use Modify attendance to change it."
        ]

    rows = [
        Attendance(student=s, subject=assignment.subject, date=date, time_slot=slot, status=status, marked_by=faculty)
        for slot in slots
        for s, status in statuses.items()
    ]
    try:
        with transaction.atomic():
            Attendance.objects.bulk_create(rows)
    except IntegrityError:
        return ["Someone saved attendance for this class at the same moment. Nothing was saved; please check and try again."]

    messages.success(
        request,
        f"Saved attendance for {len(statuses)} students, {len(slots)} slot{'s' if len(slots) > 1 else ''}, on {date:%d %b %Y}.",
    )
    return []
