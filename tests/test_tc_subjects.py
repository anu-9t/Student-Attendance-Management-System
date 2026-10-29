"""Test cases TC-Subject-01 (SAM-F-008, manage subjects) and TC-Subject-02 (SAM-F-009, assign subjects).

Test owner: Anmol Vyas (SAD Table 1). Each test logs in through the real login page.
"""
import pytest
from django.core.management import call_command

from faculty.models import Faculty
from students.models import ClassGroup
from subjects.models import Subject, SubjectAssignment, TimeSlot

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def admin(client):
    call_command("seed_data")
    assert client.post("/login/", {"username": "admin", "password": PASSWORD}).status_code == 302
    return client


# TC-Subject-01: the administrator manages subjects and time slots


def test_tc_subject_01a_add_a_subject_and_see_it_listed(admin):
    response = admin.post("/subjects/add/", {"code": "UE24CS351A", "name": "Compiler Design", "semester": 5})
    assert response.status_code == 302
    assert b"UE24CS351A" in admin.get("/subjects/").content


def test_tc_subject_01b_edit_keeps_the_same_record(admin):
    subject = Subject.objects.get(code="UE24CS343A")
    admin.post(f"/subjects/{subject.pk}/edit/", {"code": "UE24CS343A", "name": "DBMS", "semester": 5})
    subject.refresh_from_db()
    assert subject.name == "DBMS"
    assert Subject.objects.filter(code="UE24CS343A").count() == 1


def test_tc_subject_01c_duplicate_code_is_refused_with_a_message(admin):
    response = admin.post("/subjects/add/", {"code": "UE24CS341A", "name": "Copy", "semester": 5})
    assert response.status_code == 200
    assert b"already exists" in response.content


def test_tc_subject_01d_time_slot_must_end_after_it_starts(admin):
    response = admin.post("/subjects/time-slots/add/", {"label": "Bad", "start_time": "11:00", "end_time": "10:00"})
    assert response.status_code == 200
    assert not TimeSlot.objects.filter(label="Bad").exists()


# TC-Subject-02: the administrator assigns subjects to faculty, per class


def test_tc_subject_02a_assign_and_see_it_on_the_faculty_dashboard(admin, client):
    member = Faculty.objects.get(employee_id="F002")
    subject = Subject.objects.get(code="UE24CS341A")
    group = ClassGroup.objects.get(name="CSE-5B")
    admin.post("/subjects/assignments/", {"faculty": member.pk, "subject": subject.pk, "class_group": group.pk})
    assert SubjectAssignment.objects.filter(faculty=member, subject=subject, class_group=group).exists()

    admin.post("/logout/")
    client.post("/login/", {"username": "faculty2", "password": PASSWORD})
    assert b"UE24CS341A" in client.get("/dashboard/faculty/").content


def test_tc_subject_02b_the_same_assignment_twice_is_refused(admin):
    a = SubjectAssignment.objects.first()
    admin.post("/subjects/assignments/", {"faculty": a.faculty_id, "subject": a.subject_id, "class_group": a.class_group_id})
    assert SubjectAssignment.objects.filter(
        faculty=a.faculty_id, subject=a.subject_id, class_group=a.class_group_id
    ).count() == 1


def test_tc_subject_02c_removing_an_assignment_stops_marking(admin, client):
    a = SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()
    admin.post(f"/subjects/assignments/{a.pk}/remove/")
    admin.post("/logout/")
    client.post("/login/", {"username": "faculty1", "password": PASSWORD})
    assert client.get(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/").status_code == 404


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_tc_subject_02d_only_the_admin_assigns(client, username):
    call_command("seed_data")
    client.post("/login/", {"username": username, "password": PASSWORD})
    assert client.get("/subjects/assignments/").status_code == 403
