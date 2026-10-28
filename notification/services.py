"""The low-attendance threshold (SAM-F-017). Stored in SystemSetting; 75% if never set."""
from decimal import Decimal, InvalidOperation

from audit.services import record

from .models import SystemSetting

KEY = "attendance_threshold"
DEFAULT = 75.0


def get_threshold():
    value = SystemSetting.objects.filter(key=KEY).values_list("value", flat=True).first()
    try:
        return float(Decimal(value)) if value is not None else DEFAULT
    except InvalidOperation:
        return DEFAULT


def set_threshold(value, user):
    old = get_threshold()
    SystemSetting.objects.update_or_create(key=KEY, defaults={"value": f"{value:g}"})
    record(user, "Changed the attendance threshold", detail=f"{old:g}% -> {value:g}%")


def is_below(percent, threshold=None):
    """True when there were classes and the percentage is under the threshold."""
    if percent is None:
        return False
    return percent < (get_threshold() if threshold is None else threshold)


def low_subjects(student):
    """The student's subjects that are below the threshold (SubjectAttendance rows)."""
    from calculation.services import student_summary

    threshold = get_threshold()
    return [r for r in student_summary(student) if is_below(r.percent, threshold)]


def flagged_students(assignments):
    """For each class/subject a faculty member teaches: the active students below the threshold.

    Returns a list of (assignment, [(student, percent), ...]) with only the assignments that have someone flagged.
    """
    from calculation.services import percentage, subject_summary
    from students.models import Student

    threshold = get_threshold()
    result = []
    for a in assignments:
        students = list(Student.objects.filter(class_group=a.class_group, is_active=True))
        counts = subject_summary(a.subject, students)
        below = []
        for s in students:
            attended, total = counts.get(s.pk, (0, 0))
            pct = percentage(attended, total)
            if is_below(pct, threshold):
                below.append((s, pct))
        if below:
            result.append((a, sorted(below, key=lambda pair: pair[1])))
    return result
