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
