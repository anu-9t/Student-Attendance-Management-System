import datetime as dt

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction

from accounts.models import User
from attendance.models import Attendance
from audit.models import AuditLog
from faculty.models import Faculty
from notification.models import SystemSetting
from students.models import Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db


def test_health_endpoint(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seed_is_repeatable():
    call_command("seed_data")
    call_command("seed_data")
    assert TimeSlot.objects.count() == 6
    assert Student.objects.count() == 8
    assert Faculty.objects.count() == 2
    assert Subject.objects.count() == 3
    assert SystemSetting.objects.get(key="attendance_threshold").value == "75"
    assert User.objects.get(username="admin").check_password("Sams@12345")
    assert User.objects.get(username="student8").check_password("Sams@12345")


def test_seed_assigns_subjects_to_faculty():
    from subjects.models import SubjectAssignment

    call_command("seed_data")
    assert SubjectAssignment.objects.count() == 4
    faculty_one = Faculty.objects.get(employee_id="F001")
    assert set(faculty_one.assignments.values_list("class_group__name", flat=True)) == {"CSE-5A", "CSE-5B"}


def test_attendance_unique_per_student_subject_date_slot():
    call_command("seed_data")
    kwargs = dict(
        student=Student.objects.first(), subject=Subject.objects.first(),
        date=dt.date(2026, 10, 26), time_slot=TimeSlot.objects.first(),
        status=Attendance.Status.PRESENT, marked_by=Faculty.objects.first(),
    )
    Attendance.objects.create(**kwargs)
    with pytest.raises(IntegrityError), transaction.atomic():
        Attendance.objects.create(**kwargs)


def test_two_hour_lab_is_two_rows():
    call_command("seed_data")
    s1, s2 = TimeSlot.objects.all()[:2]
    for slot in (s1, s2):
        Attendance.objects.create(
            student=Student.objects.first(), subject=Subject.objects.first(),
            date=dt.date(2026, 10, 26), time_slot=slot,
            status=Attendance.Status.PRESENT, marked_by=Faculty.objects.first(),
        )
    assert Attendance.objects.count() == 2


def test_audit_log_is_append_only():
    entry = AuditLog.objects.create(action="TEST", outcome=AuditLog.Outcome.SUCCESS)
    with pytest.raises(PermissionError):
        entry.delete()
    entry.detail = "changed"
    with pytest.raises(PermissionError):
        entry.save()
