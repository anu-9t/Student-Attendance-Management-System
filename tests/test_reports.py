"""SAM-F-018 / SAM-F-019 / UC-06: attendance reports."""
import datetime as dt

import pytest
from django.core.management import call_command

from accounts.models import User
from attendance.models import Attendance
from faculty.models import Faculty
from reports import services
from students.models import ClassGroup, Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


def mark(srn, code, day, status, slot="Period 1"):
    Attendance.objects.create(
        student=Student.objects.get(srn=srn),
        subject=Subject.objects.get(code=code),
        date=dt.date(2026, 10, day),
        time_slot=TimeSlot.objects.get(label=slot),
        status=status,
        marked_by=Faculty.objects.first(),
    )


def cse5a():
    return ClassGroup.objects.get(name="CSE-5A")


def se():
    return Subject.objects.get(code="UE24CS341A")


def login(client, username):
    client.force_login(User.objects.get(username=username))


# The numbers


def test_subject_report_counts_each_student(seeded):
    mark("PES2UG24CS091", "UE24CS341A", 20, "PRESENT")
    mark("PES2UG24CS091", "UE24CS341A", 21, "ABSENT")
    report = services.subject_report(cse5a(), se())
    row = next(r for r in report.rows if r[0] == "PES2UG24CS091")
    assert row[2:] == [1, 2, "50.0%"]
    untouched = next(r for r in report.rows if r[0] == "PES2UG24CS092")
    assert untouched[2:] == [0, 0, "-"]


def test_date_range_limits_the_counts(seeded):
    mark("PES2UG24CS091", "UE24CS341A", 20, "PRESENT")
    mark("PES2UG24CS091", "UE24CS341A", 27, "ABSENT")
    report = services.subject_report(cse5a(), se(), dt.date(2026, 10, 25), None)
    row = next(r for r in report.rows if r[0] == "PES2UG24CS091")
    assert row[2:] == [0, 1, "0.0%"]
    assert "from 25 Oct 2026" in report.subtitle


def test_class_report_has_a_column_per_subject_and_overall(seeded):
    mark("PES2UG24CS091", "UE24CS341A", 20, "PRESENT")
    mark("PES2UG24CS091", "UE24CS342A", 20, "ABSENT", slot="Period 3")
    subjects = Subject.objects.filter(code__in=["UE24CS341A", "UE24CS342A"]).order_by("code")
    report = services.class_report(cse5a(), subjects)
    assert report.columns == ["SRN", "Name", "UE24CS341A", "UE24CS342A", "Overall"]
    row = next(r for r in report.rows if r[0] == "PES2UG24CS091")
    assert row[2:] == ["100.0%", "0.0%", "50.0%"]


def test_deactivated_students_are_left_out(seeded):
    Student.objects.filter(srn="PES2UG24CS092").update(is_active=False)
    srns = [r[0] for r in services.subject_report(cse5a(), se()).rows]
    assert "PES2UG24CS092" not in srns


# The pages and who may open them


def test_faculty_open_the_report_for_their_subject(client, seeded):
    mark("PES2UG24CS091", "UE24CS341A", 20, "PRESENT")
    login(client, "faculty1")
    response = client.get(f"/reports/subject/{cse5a().pk}/{se().pk}/")
    assert response.status_code == 200
    assert b"100.0%" in response.content


def test_faculty_cannot_open_a_subject_they_dont_teach(client, seeded):
    login(client, "faculty2")
    assert client.get(f"/reports/subject/{cse5a().pk}/{se().pk}/").status_code == 403


def test_faculty_class_report_shows_only_their_subjects(client, seeded):
    login(client, "faculty2")
    body = client.get(f"/reports/class/{cse5a().pk}/").content.decode()
    assert "UE24CS342A" in body and "UE24CS341A" not in body


def test_admin_class_report_shows_every_subject_of_the_class(client, seeded):
    login(client, "admin")
    body = client.get(f"/reports/class/{cse5a().pk}/").content.decode()
    assert "UE24CS341A" in body and "UE24CS342A" in body


def test_faculty_cannot_open_a_class_they_dont_teach(client, seeded):
    other = ClassGroup.objects.create(name="ME-3A", department="ME", semester=3)
    login(client, "faculty1")
    assert client.get(f"/reports/class/{other.pk}/").status_code == 403


def test_students_cannot_open_reports(client, seeded):
    login(client, "student1")
    assert client.get(f"/reports/subject/{cse5a().pk}/{se().pk}/").status_code == 403
    assert client.get(f"/reports/class/{cse5a().pk}/").status_code == 403


def test_bad_dates_are_ignored(client, seeded):
    login(client, "admin")
    assert client.get(f"/reports/class/{cse5a().pk}/", {"date_from": "yesterday"}).status_code == 200


# Student-wise report and the reports page


def test_student_report_lists_each_subject_and_overall(seeded):
    mark("PES2UG24CS091", "UE24CS341A", 20, "PRESENT")
    mark("PES2UG24CS091", "UE24CS342A", 20, "ABSENT", slot="Period 3")
    student = Student.objects.get(srn="PES2UG24CS091")
    subjects = Subject.objects.filter(code__in=["UE24CS341A", "UE24CS342A"]).order_by("code")
    report = services.student_report(student, subjects)
    assert [r[0] for r in report.rows] == ["UE24CS341A", "UE24CS342A", "Overall"]
    assert report.rows[-1][2:] == [1, 2, "50.0%"]


def test_faculty_student_report_shows_only_their_subjects(client, seeded):
    student = Student.objects.get(srn="PES2UG24CS091")
    login(client, "faculty2")
    body = client.get(f"/reports/student/{student.pk}/").content.decode()
    assert "UE24CS342A" in body and "UE24CS341A" not in body


def test_student_report_follows_the_ownership_rules(client, seeded):
    outsider = Student.objects.create(
        class_group=ClassGroup.objects.create(name="ME-3A", department="ME", semester=3), srn="PES2UG24ME002", name="X"
    )
    login(client, "faculty1")
    assert client.get(f"/reports/student/{outsider.pk}/").status_code == 403
    login(client, "admin")
    assert client.get(f"/reports/student/{outsider.pk}/").status_code == 200


def test_reports_page_lists_only_the_faculty_members_own_subjects(client, seeded):
    login(client, "faculty2")
    body = client.get("/reports/").content.decode()
    assert "UE24CS342A" in body and "UE24CS341A" not in body


def test_reports_page_finds_students(client, seeded):
    login(client, "admin")
    body = client.get("/reports/", {"q": "PES2UG24CS091"}).content.decode()
    student = Student.objects.get(srn="PES2UG24CS091")
    assert f"/reports/student/{student.pk}/" in body


@pytest.mark.parametrize("username,dashboard", [("admin", "admin"), ("faculty1", "faculty")])
def test_dashboards_link_to_reports(client, seeded, username, dashboard):
    login(client, username)
    assert b'href="/reports/"' in client.get(f"/dashboard/{dashboard}/").content
