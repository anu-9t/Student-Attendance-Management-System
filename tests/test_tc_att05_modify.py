"""Test cases TC-Att-05 (SAM-F-014, attendance modification) and an end-to-end run of UC-01.

Test owner: Anupam (SAD Table 1: UC-01, UC-02 and attendance modification).
Everything goes through the real pages, logged in as a user would be.
"""
import pytest
from django.core.management import call_command

from attendance.models import Attendance
from audit.models import AuditLog
from students.models import Student
from subjects.models import SubjectAssignment, TimeSlot

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"
DAY = "2026-10-23"


def login(client, username):
    client.post("/logout/")
    assert client.post("/login/", {"username": username, "password": PASSWORD}).status_code == 302


def own():
    return SubjectAssignment.objects.get(faculty__user__username="faculty1", class_group__name="CSE-5A")


def mark_all_present(client, a, slot):
    data = {"date": DAY, "slots": [slot.pk]}
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        data[f"status_{s.pk}"] = "PRESENT"
    assert client.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", data).status_code == 302


def modify(client, a, slot, changes, reason):
    data = {"date": DAY, "slot": slot.pk, "reason": reason}
    for row in Attendance.objects.filter(subject=a.subject, date=DAY, time_slot=slot):
        data[f"status_{row.pk}"] = changes.get(row.student.srn, row.status)
    return client.post(f"/attendance/modify/{a.class_group_id}/{a.subject_id}/", data)


@pytest.fixture
def marked(client):
    call_command("seed_data")
    login(client, "faculty1")
    slot = TimeSlot.objects.get(label="Period 2")
    mark_all_present(client, own(), slot)
    return client, slot


def test_tc_att05_01_correct_one_student_with_a_reason(marked):
    client, slot = marked
    response = modify(client, own(), slot, {"PES2UG24CS093": "ABSENT"}, "Was at the placement talk, not in class")
    assert response.status_code == 302
    assert Attendance.objects.get(student__srn="PES2UG24CS093", date=DAY).status == "ABSENT"
    assert Attendance.objects.filter(date=DAY, status="PRESENT").count() == 3


def test_tc_att05_02_no_reason_no_change(marked):
    client, slot = marked
    response = modify(client, own(), slot, {"PES2UG24CS093": "ABSENT"}, "")
    assert b"Please give a reason" in response.content
    assert not Attendance.objects.filter(status="ABSENT").exists()


def test_tc_att05_03_audit_entry_has_who_what_and_why(marked):
    client, slot = marked
    modify(client, own(), slot, {"PES2UG24CS093": "ABSENT"}, "Medical certificate submitted late")
    entry = AuditLog.objects.get(action="Changed attendance")
    assert entry.user.username == "faculty1"
    assert "PES2UG24CS093" in entry.detail and "PRESENT -> ABSENT" in entry.detail
    assert "Medical certificate submitted late" in entry.detail


def test_tc_att05_04_several_changes_are_saved_together(marked):
    client, slot = marked
    modify(client, own(), slot, {"PES2UG24CS091": "ABSENT", "PES2UG24CS093": "ABSENT"}, "Both left at the break")
    assert Attendance.objects.filter(date=DAY, status="ABSENT").count() == 2
    assert AuditLog.objects.filter(action="Changed attendance").count() == 2


def test_tc_att05_05_another_faculty_member_cannot_modify(marked):
    client, slot = marked
    login(client, "faculty2")
    response = modify(client, own(), slot, {"PES2UG24CS093": "ABSENT"}, "Trying someone else's class")
    assert response.status_code == 404
    assert not Attendance.objects.filter(status="ABSENT").exists()


def test_tc_att05_06_the_change_shows_in_percentage_and_history(marked):
    client, slot = marked
    modify(client, own(), slot, {"PES2UG24CS091": "ABSENT"}, "Marked present by mistake")
    login(client, "student1")  # PES2UG24CS091
    assert b"0.0%" in client.get("/percentage/").content
    assert b"Absent" in client.get("/history/").content


# UC-01 end to end: select, mark, check, correct


def test_tc_uc01_08_full_flow_from_login_to_report(client):
    call_command("seed_data")
    login(client, "faculty1")
    a = own()
    page = client.get("/attendance/select/", {"class_id": a.class_group_id, "subject_id": a.subject_id})
    assert f"/attendance/mark/{a.class_group_id}/{a.subject_id}/".encode() in page.content

    slot = TimeSlot.objects.get(label="Period 1")
    mark_all_present(client, a, slot)
    modify(client, a, slot, {"PES2UG24CS094": "ABSENT"}, "Left after roll call")

    report = client.get(f"/reports/subject/{a.class_group_id}/{a.subject_id}/").content.decode()
    row = report[report.index("PES2UG24CS094"):]
    assert "0.0%" in row[: row.index("</tr>")]
