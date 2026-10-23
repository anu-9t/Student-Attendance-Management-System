"""Test cases for UC-04 (Manage User Access). Test owner: Anupriya (STP Section 9)."""
import pytest
from django.core.management import call_command

from accounts.models import User
from faculty.models import Faculty
from students.models import Student

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def seeded():
    call_command("seed_data")


def login(client, username):
    return client.post("/login/", {"username": username, "password": PASSWORD})


def test_tc_uc04_01_admin_reaches_every_management_page(client, seeded):
    login(client, "admin")
    for url in ["/students/", "/faculty/", "/subjects/", "/subjects/time-slots/", "/subjects/assignments/"]:
        assert client.get(url).status_code == 200, url


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_tc_uc04_02_other_roles_cannot_reach_management_pages(client, seeded, username):
    login(client, username)
    for url in ["/students/", "/faculty/", "/subjects/", "/subjects/assignments/"]:
        assert client.get(url).status_code == 403, url


def test_tc_uc04_03_deactivated_student_cannot_log_in(client, seeded):
    login(client, "admin")
    student = Student.objects.get(user__username="student1")
    client.post(f"/students/{student.pk}/deactivate/")
    client.post("/logout/")
    response = login(client, "student1")
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_tc_uc04_04_deactivated_faculty_cannot_log_in(client, seeded):
    login(client, "admin")
    member = Faculty.objects.get(user__username="faculty2")
    client.post(f"/faculty/{member.pk}/deactivate/")
    client.post("/logout/")
    login(client, "faculty2")
    assert "_auth_user_id" not in client.session


def test_tc_uc04_05_new_student_gets_a_working_login(client, seeded):
    from students.models import ClassGroup

    login(client, "admin")
    group = ClassGroup.objects.get(name="CSE-5B")
    client.post("/students/add/", {"srn": "PES2UG24CS150", "name": "New One", "email": "",
                                   "class_group": group.pk, "password": "Welcome@123"})
    client.post("/logout/")
    response = client.post("/login/", {"username": "PES2UG24CS150", "password": "Welcome@123"})
    assert response.status_code == 302
    assert client.get("/", follow=True).redirect_chain[-1][0] == "/dashboard/student/"


def test_tc_uc04_06_each_role_only_opens_its_own_dashboard(client, seeded):
    login(client, "student1")
    assert client.get("/dashboard/student/").status_code == 200
    assert client.get("/dashboard/faculty/").status_code == 403
    assert client.get("/dashboard/admin/").status_code == 403


def test_tc_uc04_07_roles_are_stored_on_the_account(seeded):
    assert User.objects.get(username="admin").role == User.Role.ADMIN
    assert User.objects.get(username="faculty1").role == User.Role.FACULTY
    assert User.objects.get(username="student8").role == User.Role.STUDENT
