"""SAM-F-016 / UC-07: attendance history, newest first."""
import datetime as dt

import pytest
from django.core.management import call_command

from accounts.models import User
from attendance.models import Attendance
from faculty.models import Faculty
from students.models import Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


def mark(student, code, day, slot_label, status="PRESENT"):
    return Attendance.objects.create(
        student=student,
        subject=Subject.objects.get(code=code),
        date=dt.date(2026, 10, day),
        time_slot=TimeSlot.objects.get(label=slot_label),
        status=status,
        marked_by=Faculty.objects.first(),
    )


def me():
    return Student.objects.get(user__username="student1")


def test_student_sees_their_history_newest_first(client, seeded):
    mark(me(), "UE24CS341A", 20, "Period 1")
    mark(me(), "UE24CS342A", 22, "Period 3", "ABSENT")
    mark(me(), "UE24CS341A", 22, "Period 1")
    client.force_login(me().user)
    body = client.get("/history/").content.decode()
    assert body.index("Thu 22 Oct 2026") < body.index("Tue 20 Oct 2026")
    # same day: the later slot comes first
    assert body.index("Period 3") < body.index("Period 1")
    assert "Absent" in body


def test_history_shows_only_their_own_records(client, seeded):
    other = Student.objects.get(user__username="student2")
    mark(other, "UE24CS341A", 20, "Period 1", "ABSENT")
    client.force_login(me().user)
    body = client.get("/history/").content.decode()
    assert "No attendance has been recorded yet" in body


def test_dashboard_links_to_history(client, seeded):
    client.force_login(me().user)
    assert b'href="/history/"' in client.get("/dashboard/student/").content


@pytest.mark.parametrize("username", ["admin", "faculty1"])
def test_own_history_page_is_for_students(client, seeded, username):
    client.force_login(User.objects.get(username=username))
    assert client.get("/history/").status_code == 403
