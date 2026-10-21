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
