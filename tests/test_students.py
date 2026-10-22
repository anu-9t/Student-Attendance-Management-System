import pytest
from django.core.management import call_command

from accounts.models import User
from students.models import ClassGroup, Student

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="admin"))
    return client


# SAM-F-004: add a student


def test_admin_sees_the_student_list(admin_client):
    response = admin_client.get("/students/")
    assert response.status_code == 200
    assert b"PES2UG24CS091" in response.content


def test_admin_adds_a_student_with_a_login(admin_client):
    group = ClassGroup.objects.get(name="CSE-5A")
    response = admin_client.post(
        "/students/add/",
        {"srn": "pes2ug24cs199", "name": "New Student", "email": "new@example.com",
         "class_group": group.id, "password": "Welcome@123"},
    )
    assert response.status_code == 302
    student = Student.objects.get(srn="PES2UG24CS199")
    assert student.user.username == "PES2UG24CS199"
    assert student.user.role == User.Role.STUDENT
    assert student.user.check_password("Welcome@123")


def test_duplicate_srn_is_rejected(admin_client):
    group = ClassGroup.objects.get(name="CSE-5A")
    response = admin_client.post(
        "/students/add/",
        {"srn": "PES2UG24CS091", "name": "Copy", "email": "", "class_group": group.id, "password": "Welcome@123"},
    )
    assert response.status_code == 200
    assert Student.objects.filter(srn="PES2UG24CS091").count() == 1


def test_faculty_cannot_add_students(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    assert client.get("/students/add/").status_code == 403


# SAM-F-005 and SAM-F-006: update and search


def test_admin_updates_a_student(admin_client):
    student = Student.objects.get(srn="PES2UG24CS091")
    response = admin_client.post(
        f"/students/{student.pk}/edit/",
        {"srn": student.srn, "name": "Renamed Student", "email": "renamed@example.com",
         "class_group": student.class_group_id},
    )
    assert response.status_code == 302
    student.refresh_from_db()
    assert student.name == "Renamed Student"


def test_search_by_srn_and_by_name(admin_client):
    response = admin_client.get("/students/", {"q": "cs092"})
    assert b"PES2UG24CS092" in response.content
    assert b"PES2UG24CS093" not in response.content
    response = admin_client.get("/students/", {"q": "Student 3"})
    assert b"PES2UG24CS093" in response.content


# Deactivate instead of delete (ADR-003)


def test_deactivated_student_is_hidden_and_cannot_log_in(admin_client):
    student = Student.objects.get(srn="PES2UG24CS091")
    response = admin_client.post(f"/students/{student.pk}/deactivate/")
    assert response.status_code == 302
    student.refresh_from_db()
    assert student.is_active is False
    assert Student.objects.filter(pk=student.pk).exists()
    assert b"PES2UG24CS091" not in admin_client.get("/students/").content
    assert b"PES2UG24CS091" in admin_client.get("/students/", {"show": "all"}).content

    student.user.refresh_from_db()
    assert student.user.is_active is False  # Django refuses logins for inactive users


def test_deactivate_needs_a_post(admin_client):
    student = Student.objects.get(srn="PES2UG24CS092")
    admin_client.get(f"/students/{student.pk}/deactivate/")
    student.refresh_from_db()
    assert student.is_active is True
