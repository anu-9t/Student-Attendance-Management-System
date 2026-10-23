"""Test cases for UC-01 (Mark Attendance) and UC-02 (Select Class and Subject).

Written by the test owner for these use cases (STP Section 9, SAD Table 1).
Each test goes through the real login page, as a user would.
"""
import pytest
from django.core.management import call_command

from attendance.models import Attendance
from students.models import Student
from subjects.models import SubjectAssignment, TimeSlot

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def faculty1(client):
    call_command("seed_data")
    response = client.post("/login/", {"username": "faculty1", "password": PASSWORD})
    assert response.status_code == 302
    return client


def own(username="faculty1"):
    return SubjectAssignment.objects.filter(faculty__user__username=username).first()


def full_sheet(a, slots, date="2026-10-23", absent=()):
    data = {"date": date, "slots": [s.pk for s in slots]}
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        data[f"status_{s.pk}"] = "ABSENT" if s.srn in absent else "PRESENT"
    return data


# UC-02: Select Class and Subject


def test_tc_uc02_01_login_lands_on_the_faculty_dashboard(faculty1):
    response = faculty1.get("/", follow=True)
    assert response.redirect_chain[-1][0] == "/dashboard/faculty/"


def test_tc_uc02_02_only_assigned_pairs_are_offered(faculty1):
    response = faculty1.get("/attendance/select/")
    for a in SubjectAssignment.objects.filter(faculty__user__username="faculty1"):
        assert f"{a.class_group.name}".encode() in response.content
    assert b"UE24CS342A" not in response.content  # taught by faculty2


def test_tc_uc02_03_a_student_cannot_select(client):
    call_command("seed_data")
    client.post("/login/", {"username": "student1", "password": PASSWORD})
    assert client.get("/attendance/select/").status_code == 403


# UC-01: Mark Attendance


def test_tc_uc01_01_mark_and_save_a_one_hour_class(faculty1):
    a = own()
    p1 = TimeSlot.objects.get(label="Period 1")
    faculty1.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", full_sheet(a, [p1], absent={"PES2UG24CS093"}))
    assert Attendance.objects.filter(date="2026-10-23", time_slot=p1).count() == 4
    assert Attendance.objects.get(student__srn="PES2UG24CS093").status == "ABSENT"


def test_tc_uc01_02_a_two_hour_lab_counts_as_two_classes(faculty1):
    a = own()
    lab = TimeSlot.objects.filter(label__in=["Period 4", "Period 5"])
    faculty1.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", full_sheet(a, lab))
    assert Attendance.objects.filter(student__srn="PES2UG24CS091").count() == 2


def test_tc_uc01_03_the_same_slot_cannot_be_marked_twice(faculty1):
    a = own()
    p1 = TimeSlot.objects.get(label="Period 1")
    url = f"/attendance/mark/{a.class_group_id}/{a.subject_id}/"
    faculty1.post(url, full_sheet(a, [p1]))
    response = faculty1.post(url, full_sheet(a, [p1], absent={"PES2UG24CS091"}))
    assert b"already saved" in response.content
    assert Attendance.objects.get(student__srn="PES2UG24CS091").status == "PRESENT"


def test_tc_uc01_04_two_subjects_in_the_same_slot_are_separate(faculty1, client):
    a = own()
    p1 = TimeSlot.objects.get(label="Period 1")
    faculty1.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", full_sheet(a, [p1]))
    client.post("/logout/")
    client.post("/login/", {"username": "faculty2", "password": PASSWORD})
    b = SubjectAssignment.objects.get(faculty__user__username="faculty2", class_group=a.class_group)
    client.post(f"/attendance/mark/{b.class_group_id}/{b.subject_id}/", full_sheet(b, [p1]))
    assert Attendance.objects.filter(student__srn="PES2UG24CS091", date="2026-10-23").count() == 2


def test_tc_uc01_05_deactivated_students_are_not_on_the_sheet(faculty1):
    a = own()
    Student.objects.filter(srn="PES2UG24CS094").update(is_active=False)
    response = faculty1.get(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/")
    assert b"PES2UG24CS094" not in response.content


def test_tc_uc01_06_cannot_mark_another_faculty_members_class(faculty1):
    other = own("faculty2")
    p1 = TimeSlot.objects.get(label="Period 1")
    response = faculty1.post(f"/attendance/mark/{other.class_group_id}/{other.subject_id}/", full_sheet(other, [p1]))
    assert response.status_code == 404
    assert Attendance.objects.count() == 0


def test_tc_uc01_07_logged_out_users_go_to_login(client):
    call_command("seed_data")
    a = own()
    response = client.get(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/")
    assert response.status_code == 302 and response.url.startswith("/login/")
