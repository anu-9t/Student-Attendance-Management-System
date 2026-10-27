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


# Filtering, pages, and who else can open a student's history


def test_history_can_be_filtered_by_subject(client, seeded):
    mark(me(), "UE24CS341A", 20, "Period 1")
    mark(me(), "UE24CS342A", 21, "Period 3")
    client.force_login(me().user)
    se = Subject.objects.get(code="UE24CS341A")
    body = client.get("/history/", {"subject": se.pk}).content.decode()
    assert "Tue 20 Oct 2026" in body and "Wed 21 Oct 2026" not in body


def test_long_history_is_split_into_pages(client, seeded):
    slots = list(TimeSlot.objects.all())
    for day in range(1, 7):  # 36 classes, 25 to a page
        for slot in slots:
            mark(me(), "UE24CS341A", day, slot.label)
    client.force_login(me().user)
    first = client.get("/history/").content.decode()
    assert "Page 1 of 2" in first
    assert "Tue 06 Oct 2026" in first and "Thu 01 Oct 2026" not in first
    assert "Thu 01 Oct 2026" in client.get("/history/", {"page": 2}).content.decode()


def test_faculty_open_the_history_of_a_student_they_teach(client, seeded):
    mark(me(), "UE24CS341A", 20, "Period 1")
    client.force_login(User.objects.get(username="faculty1"))
    response = client.get(f"/history/student/{me().pk}/")
    assert response.status_code == 200
    assert me().srn.encode() in response.content


def test_admin_opens_any_students_history(client, seeded):
    client.force_login(User.objects.get(username="admin"))
    assert client.get(f"/history/student/{me().pk}/").status_code == 200


def test_a_student_cannot_open_someone_elses_history(client, seeded):
    other = Student.objects.get(user__username="student2")
    client.force_login(me().user)
    assert client.get(f"/history/student/{other.pk}/").status_code == 403


def test_faculty_cannot_open_a_student_they_dont_teach(client, seeded):
    from students.models import ClassGroup

    elsewhere = Student.objects.create(
        class_group=ClassGroup.objects.create(name="ME-3A", department="ME", semester=3),
        srn="PES2UG24ME001",
        name="Other Department",
    )
    client.force_login(User.objects.get(username="faculty2"))
    assert client.get(f"/history/student/{elsewhere.pk}/").status_code == 403
