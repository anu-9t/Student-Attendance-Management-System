"""SAM-F-015: attendance percentage per subject."""
import datetime as dt

import pytest
from django.core.management import call_command

from attendance.models import Attendance
from calculation.services import overall, percentage, student_summary, subject_summary
from faculty.models import Faculty
from students.models import Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db

P, A = Attendance.Status.PRESENT, Attendance.Status.ABSENT


@pytest.fixture
def seeded():
    call_command("seed_data")


def mark(student, code, day, slot_label, status):
    Attendance.objects.create(
        student=student,
        subject=Subject.objects.get(code=code),
        date=dt.date(2026, 10, day),
        time_slot=TimeSlot.objects.get(label=slot_label),
        status=status,
        marked_by=Faculty.objects.first(),
    )


def test_percentage_rounds_to_one_decimal():
    assert percentage(2, 3) == 66.7
    assert percentage(3, 3) == 100.0
    assert percentage(0, 4) == 0.0


def test_no_classes_means_no_percentage():
    assert percentage(0, 0) is None


def test_each_slot_counts_as_one_class(seeded):
    s = Student.objects.get(user__username="student1")
    # a two-hour lab: two slots, both present; then one absent theory class
    mark(s, "UE24CS341A", 20, "Period 1", P)
    mark(s, "UE24CS341A", 20, "Period 2", P)
    mark(s, "UE24CS341A", 21, "Period 1", A)
    row = next(r for r in student_summary(s) if r.subject.code == "UE24CS341A")
    assert (row.attended, row.total, row.percent) == (2, 3, 66.7)


def test_subjects_without_classes_are_listed_with_no_percentage(seeded):
    s = Student.objects.get(user__username="student1")
    rows = student_summary(s)
    assert {r.subject.code for r in rows} == {"UE24CS341A", "UE24CS342A"}  # what CSE-5A is taught
    assert all(r.percent is None for r in rows)


def test_overall_adds_up_every_subject(seeded):
    s = Student.objects.get(user__username="student1")
    mark(s, "UE24CS341A", 20, "Period 1", P)
    mark(s, "UE24CS342A", 20, "Period 3", A)
    assert overall(student_summary(s)) == {"attended": 1, "total": 2, "percent": 50.0}


def test_one_students_marks_dont_affect_another(seeded):
    me = Student.objects.get(user__username="student1")
    other = Student.objects.get(user__username="student2")
    mark(other, "UE24CS341A", 20, "Period 1", P)
    assert overall(student_summary(me))["total"] == 0


def test_subject_summary_for_a_class(seeded):
    se = Subject.objects.get(code="UE24CS341A")
    students = list(Student.objects.filter(class_group__name="CSE-5A"))
    mark(students[0], "UE24CS341A", 20, "Period 1", P)
    mark(students[1], "UE24CS341A", 20, "Period 1", A)
    summary = subject_summary(se, students)
    assert summary[students[0].pk] == (1, 1)
    assert summary[students[1].pk] == (0, 1)
    assert students[2].pk not in summary


# UC-03: the student's percentage page


def test_student_sees_their_percentage_page(client, seeded):
    s = Student.objects.get(user__username="student1")
    mark(s, "UE24CS341A", 20, "Period 1", P)
    mark(s, "UE24CS341A", 21, "Period 1", A)
    client.force_login(s.user)
    body = client.get("/percentage/").content.decode()
    assert "UE24CS341A" in body
    assert "50.0%" in body
    assert "No classes yet" in body  # UE24CS342A has none


@pytest.mark.parametrize("username", ["admin", "faculty1"])
def test_page_is_for_students_only(client, seeded, username):
    from accounts.models import User

    client.force_login(User.objects.get(username=username))
    assert client.get("/percentage/").status_code == 403


def test_student_dashboard_links_to_the_page(client, seeded):
    client.force_login(Student.objects.get(user__username="student1").user)
    assert b'href="/percentage/"' in client.get("/dashboard/student/").content


def test_student_login_without_a_record_gets_a_message(client, seeded):
    from accounts.models import User

    lonely = User.objects.create_user(username="nobody", password="x", role=User.Role.STUDENT)
    client.force_login(lonely)
    assert b"isn't linked to a student record" in client.get("/percentage/").content
