"""SAM-F-017: the threshold setting and low-attendance flags."""
import pytest
from django.core.management import call_command

from accounts.models import User
from audit.models import AuditLog
from notification.models import SystemSetting
from notification.services import get_threshold, is_below

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


@pytest.fixture
def admin_client(client, seeded):
    client.force_login(User.objects.get(username="admin"))
    return client


def test_default_threshold_is_75(seeded):
    assert get_threshold() == 75.0


def test_missing_or_broken_setting_falls_back_to_75():
    assert get_threshold() == 75.0
    SystemSetting.objects.create(key="attendance_threshold", value="lots")
    assert get_threshold() == 75.0


def test_is_below():
    assert is_below(74.9, 75)
    assert not is_below(75.0, 75)
    assert not is_below(None, 75)  # no classes yet is not a warning


def test_admin_changes_the_threshold(admin_client):
    response = admin_client.post("/notifications/threshold/", {"threshold": "80"})
    assert response.status_code == 302
    assert get_threshold() == 80.0
    entry = AuditLog.objects.get(action="Changed the attendance threshold")
    assert entry.detail == "75% -> 80%"


@pytest.mark.parametrize("value", ["-1", "101", "abc"])
def test_threshold_must_be_a_percentage(admin_client, value):
    response = admin_client.post("/notifications/threshold/", {"threshold": value})
    assert response.status_code == 200
    assert get_threshold() == 75.0


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_only_the_admin_sets_it(client, seeded, username):
    client.force_login(User.objects.get(username=username))
    assert client.post("/notifications/threshold/", {"threshold": "10"}).status_code == 403
    assert get_threshold() == 75.0


def test_admin_dashboard_links_to_the_setting(admin_client):
    assert b'href="/notifications/threshold/"' in admin_client.get("/dashboard/admin/").content


# Low-attendance flags


def mark_many(student, code, present, absent):
    import datetime as dt

    from attendance.models import Attendance
    from faculty.models import Faculty
    from subjects.models import Subject, TimeSlot

    subject = Subject.objects.get(code=code)
    slot = TimeSlot.objects.get(label="Period 1")
    faculty = Faculty.objects.first()
    statuses = ["PRESENT"] * present + ["ABSENT"] * absent
    for i, status in enumerate(statuses):
        Attendance.objects.create(
            student=student, subject=subject, date=dt.date(2026, 9, 1) + dt.timedelta(days=i),
            time_slot=slot, status=status, marked_by=faculty,
        )


def student1():
    from students.models import Student

    return Student.objects.get(user__username="student1")


def test_student_dashboard_warns_about_low_subjects(client, seeded):
    mark_many(student1(), "UE24CS341A", present=2, absent=2)   # 50%
    mark_many(student1(), "UE24CS342A", present=4, absent=0)   # 100%
    client.force_login(student1().user)
    body = client.get("/dashboard/student/").content.decode()
    assert "Low attendance" in body
    assert "UE24CS341A (50.0%)" in body
    assert "UE24CS342A (" not in body


def test_no_warning_when_everything_is_above(client, seeded):
    mark_many(student1(), "UE24CS341A", present=4, absent=0)
    client.force_login(student1().user)
    assert b"Low attendance" not in client.get("/dashboard/student/").content


def test_percentage_page_flags_the_low_subject(client, seeded):
    mark_many(student1(), "UE24CS341A", present=1, absent=3)
    client.force_login(student1().user)
    assert b"Below 75%" in client.get("/percentage/").content


def test_raising_the_threshold_flags_more(client, seeded):
    from notification.services import set_threshold

    mark_many(student1(), "UE24CS341A", present=4, absent=1)   # 80%
    client.force_login(student1().user)
    assert b"Low attendance" not in client.get("/dashboard/student/").content
    set_threshold(85, None)
    assert b"UE24CS341A (80.0%)" in client.get("/dashboard/student/").content


def test_faculty_dashboard_lists_their_students_below_the_threshold(client, seeded):
    mark_many(student1(), "UE24CS341A", present=1, absent=1)
    client.force_login(User.objects.get(username="faculty1"))
    body = client.get("/dashboard/faculty/").content.decode()
    assert "Students below 75%" in body
    assert f'href="/history/student/{student1().pk}/"' in body


def test_other_faculty_dont_see_students_they_dont_teach(client, seeded):
    mark_many(student1(), "UE24CS341A", present=1, absent=1)
    client.force_login(User.objects.get(username="faculty2"))
    assert b"Students below" not in client.get("/dashboard/faculty/").content
