import pytest
from django.core.management import call_command

from accounts.models import User
from subjects.models import Subject

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="admin"))
    return client


# SAM-F-008: manage subjects


def test_admin_sees_subjects(admin_client):
    response = admin_client.get("/subjects/")
    assert response.status_code == 200
    assert b"UE24CS341A" in response.content


def test_admin_adds_and_edits_a_subject(admin_client):
    admin_client.post("/subjects/add/", {"code": "ue24cs344a", "name": "Compiler Design", "semester": 5})
    subject = Subject.objects.get(code="UE24CS344A")
    admin_client.post(f"/subjects/{subject.pk}/edit/", {"code": "UE24CS344A", "name": "Compilers", "semester": 5})
    subject.refresh_from_db()
    assert subject.name == "Compilers"


def test_duplicate_subject_code_is_rejected(admin_client):
    response = admin_client.post("/subjects/add/", {"code": "UE24CS341A", "name": "Copy", "semester": 5})
    assert response.status_code == 200
    assert Subject.objects.filter(code="UE24CS341A").count() == 1


def test_faculty_cannot_manage_subjects(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    assert client.get("/subjects/").status_code == 403


# Time slots (ADR-004)


def test_admin_sees_the_six_periods(admin_client):
    response = admin_client.get("/subjects/time-slots/")
    assert response.status_code == 200
    assert b"Period 1" in response.content and b"Period 6" in response.content


def test_admin_adds_a_time_slot(admin_client):
    from subjects.models import TimeSlot

    admin_client.post("/subjects/time-slots/add/", {"label": "Period 7", "start_time": "16:00", "end_time": "17:00"})
    assert TimeSlot.objects.filter(label="Period 7").exists()


def test_a_slot_ending_before_it_starts_is_rejected(admin_client):
    from subjects.models import TimeSlot

    response = admin_client.post("/subjects/time-slots/add/", {"label": "Bad", "start_time": "11:00", "end_time": "10:00"})
    assert response.status_code == 200
    assert not TimeSlot.objects.filter(label="Bad").exists()


# SAM-F-009: assign subjects to faculty


def test_admin_assigns_a_subject_to_a_faculty_member(admin_client):
    from faculty.models import Faculty
    from students.models import ClassGroup
    from subjects.models import SubjectAssignment

    faculty = Faculty.objects.get(employee_id="F002")
    subject = Subject.objects.get(code="UE24CS341A")
    group = ClassGroup.objects.get(name="CSE-5B")
    response = admin_client.post("/subjects/assignments/", {"faculty": faculty.pk, "subject": subject.pk, "class_group": group.pk})
    assert response.status_code == 302
    assert SubjectAssignment.objects.filter(faculty=faculty, subject=subject, class_group=group).exists()


def test_the_same_assignment_cannot_be_added_twice(admin_client):
    from subjects.models import SubjectAssignment

    existing = SubjectAssignment.objects.first()
    response = admin_client.post(
        "/subjects/assignments/",
        {"faculty": existing.faculty_id, "subject": existing.subject_id, "class_group": existing.class_group_id},
    )
    assert response.status_code == 200
    assert SubjectAssignment.objects.count() == 4


def test_admin_removes_an_assignment(admin_client):
    from subjects.models import SubjectAssignment

    existing = SubjectAssignment.objects.first()
    admin_client.post(f"/subjects/assignments/{existing.pk}/remove/")
    assert SubjectAssignment.objects.count() == 3
