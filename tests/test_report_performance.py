"""SAM-NF-001: reports cost the same number of queries however big the class is."""
import datetime as dt

import pytest
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from attendance.models import Attendance
from faculty.models import Faculty
from reports import services
from students.models import ClassGroup, Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db


def build_class(name, size, days=5):
    group = ClassGroup.objects.create(name=name, department="CSE", semester=5)
    Student.objects.bulk_create(
        [Student(class_group=group, srn=f"{name}-{i:03d}", name=f"Student {i}") for i in range(size)]
    )
    subject = Subject.objects.get(code="UE24CS341A")
    slot = TimeSlot.objects.get(label="Period 1")
    marked_by = Faculty.objects.first()
    rows = [
        Attendance(student=s, subject=subject, date=dt.date(2026, 10, d), time_slot=slot, status="PRESENT",
                   marked_by=marked_by)
        for s in Student.objects.filter(class_group=group)
        for d in range(1, days + 1)
    ]
    Attendance.objects.bulk_create(rows)
    return group, subject


def queries_for(build):
    with CaptureQueriesContext(connection) as ctx:
        build()
    return len(ctx.captured_queries)


def test_subject_report_queries_dont_grow_with_the_class():
    call_command("seed_data")
    small, subject = build_class("SMALL", 3)
    big, _ = build_class("BIG", 60)
    assert queries_for(lambda: services.subject_report(small, subject)) == queries_for(
        lambda: services.subject_report(big, subject)
    )


def test_class_report_queries_dont_grow_with_the_class():
    call_command("seed_data")
    small, subject = build_class("SMALL", 3)
    big, _ = build_class("BIG", 60)
    assert queries_for(lambda: services.class_report(small, Subject.objects.filter(pk=subject.pk))) == queries_for(
        lambda: services.class_report(big, Subject.objects.filter(pk=subject.pk))
    )


def test_the_indexes_exist():
    names = {i.name for i in Attendance._meta.indexes} | {i.name for i in Student._meta.indexes}
    assert {"att_subject_student_status", "student_class_active"} <= names


# Long reports are paged on screen; low percentages stand out


def test_long_report_is_paged_but_downloads_have_every_row(client):
    from accounts.models import User

    call_command("seed_data")
    big, subject = build_class("BIG", 120, days=1)
    client.force_login(User.objects.get(username="admin"))
    first = client.get(f"/reports/subject/{big.pk}/{subject.pk}/").content.decode()
    assert "Page 1 of 3" in first
    assert "BIG-000" in first and "BIG-050" not in first
    assert "BIG-119" in client.get(f"/reports/subject/{big.pk}/{subject.pk}/", {"page": 3}).content.decode()
    csv_text = client.get(f"/reports/subject/{big.pk}/{subject.pk}/", {"format": "csv"}).content.decode("utf-8-sig")
    assert csv_text.count("BIG-") == 120


def test_percentages_below_the_threshold_are_highlighted(client):
    from accounts.models import User

    call_command("seed_data")
    group, subject = build_class("LOW", 2, days=4)
    weak = Student.objects.get(srn="LOW-000")
    Attendance.objects.filter(student=weak, date__day__in=[1, 2]).update(status="ABSENT")  # 50%
    client.force_login(User.objects.get(username="admin"))
    body = client.get(f"/reports/subject/{group.pk}/{subject.pk}/").content.decode()
    assert '<td class="text-danger fw-bold">50.0%</td>' in body
    assert "<td>100.0%</td>" in body
