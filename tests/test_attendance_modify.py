"""SAM-F-014: faculty correct attendance that was already saved."""
import datetime as dt

import pytest
from django.core.management import call_command

from accounts.models import User
from attendance.models import Attendance
from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment, TimeSlot

pytestmark = pytest.mark.django_db

DAY = dt.date(2026, 10, 23)


@pytest.fixture
def faculty_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    return client


def own_assignment():
    return SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()


def saved_sheet(a, status="PRESENT"):
    slot = TimeSlot.objects.get(label="Period 1")
    faculty = Faculty.objects.get(user__username="faculty1")
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        Attendance.objects.create(
            student=s, subject=a.subject, date=DAY, time_slot=slot, status=status, marked_by=faculty
        )
    return slot


def url(a):
    return f"/attendance/modify/{a.class_group_id}/{a.subject_id}/"


def test_page_lists_the_classes_already_marked(faculty_client):
    a = own_assignment()
    saved_sheet(a)
    body = faculty_client.get(url(a)).content.decode()
    assert "Fri 23 Oct 2026, Period 1" in body


def test_opening_a_session_shows_its_saved_statuses(faculty_client):
    a = own_assignment()
    slot = saved_sheet(a)
    response = faculty_client.get(url(a), {"date": "2026-10-23", "slot": slot.pk})
    for s in Student.objects.filter(class_group=a.class_group):
        assert s.srn.encode() in response.content


def test_select_page_links_to_modify(faculty_client):
    a = own_assignment()
    response = faculty_client.get("/attendance/select/", {"class_id": a.class_group_id, "subject_id": a.subject_id})
    assert url(a).encode() in response.content


def test_someone_elses_class_cannot_be_modified(faculty_client):
    other = SubjectAssignment.objects.exclude(faculty__user__username="faculty1").first()
    assert faculty_client.get(url(other)).status_code == 404


@pytest.mark.parametrize("username", ["admin", "student1"])
def test_only_faculty_modify(client, username):
    call_command("seed_data")
    client.force_login(User.objects.get(username=username))
    assert client.get(url(own_assignment())).status_code == 403


def change_one(faculty_client, a, slot, reason):
    row = Attendance.objects.filter(subject=a.subject, date=DAY).order_by("student__srn").first()
    data = {"date": "2026-10-23", "slot": slot.pk, "reason": reason}
    for r in Attendance.objects.filter(subject=a.subject, date=DAY):
        data[f"status_{r.pk}"] = "ABSENT" if r.pk == row.pk else r.status
    return row, faculty_client.post(url(a), data)


def test_a_change_with_a_reason_is_saved(faculty_client):
    a = own_assignment()
    slot = saved_sheet(a)
    row, response = change_one(faculty_client, a, slot, "Left before the class started")
    assert response.status_code == 302
    row.refresh_from_db()
    assert row.status == "ABSENT"
    assert Attendance.objects.filter(subject=a.subject, date=DAY, status="ABSENT").count() == 1


def test_a_change_without_a_reason_is_refused(faculty_client):
    a = own_assignment()
    slot = saved_sheet(a)
    row, response = change_one(faculty_client, a, slot, "")
    assert response.status_code == 200
    assert b"Please give a reason" in response.content
    row.refresh_from_db()
    assert row.status == "PRESENT"


def test_the_change_and_its_reason_go_to_the_audit_log(faculty_client):
    from audit.models import AuditLog

    a = own_assignment()
    slot = saved_sheet(a)
    row, _ = change_one(faculty_client, a, slot, "Medical leave approved")
    entry = AuditLog.objects.get(action="Changed attendance")
    assert entry.user.username == "faculty1"
    assert entry.target_type == "Attendance" and entry.target_id == str(row.pk)
    assert "PRESENT -> ABSENT" in entry.detail
    assert "Reason: Medical leave approved" in entry.detail


def test_saving_without_changes_says_so(faculty_client):
    a = own_assignment()
    slot = saved_sheet(a)
    data = {"date": "2026-10-23", "slot": slot.pk, "reason": "no change at all"}
    for r in Attendance.objects.filter(subject=a.subject, date=DAY):
        data[f"status_{r.pk}"] = r.status
    assert b"Nothing was changed" in faculty_client.post(url(a), data).content


def test_changing_does_not_add_rows(faculty_client):
    a = own_assignment()
    slot = saved_sheet(a)
    before = Attendance.objects.count()
    change_one(faculty_client, a, slot, "Corrected after checking the register")
    assert Attendance.objects.count() == before
