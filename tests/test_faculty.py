import pytest
from django.core.management import call_command

from accounts.models import User
from faculty.models import Faculty

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="admin"))
    return client


# SAM-F-007: manage faculty


def test_faculty_list_shows_what_each_one_teaches(admin_client):
    response = admin_client.get("/faculty/")
    assert response.status_code == 200
    assert b"F001" in response.content
    assert b"UE24CS341A (CSE-5A)" in response.content


def test_admin_adds_a_faculty_member_with_a_login(admin_client):
    response = admin_client.post(
        "/faculty/add/",
        {"employee_id": "f003", "name": "New Faculty", "department": "CSE",
         "username": "faculty3", "password": "Welcome@123"},
    )
    assert response.status_code == 302
    member = Faculty.objects.get(employee_id="F003")
    assert member.user.role == User.Role.FACULTY
    assert member.user.check_password("Welcome@123")


def test_admin_edits_and_deactivates_a_faculty_member(admin_client):
    member = Faculty.objects.get(employee_id="F002")
    admin_client.post(f"/faculty/{member.pk}/edit/", {"employee_id": "F002", "name": "Changed Name", "department": "ECE"})
    member.refresh_from_db()
    assert member.name == "Changed Name" and member.department == "ECE"

    admin_client.post(f"/faculty/{member.pk}/deactivate/")
    member.refresh_from_db()
    assert member.is_active is False and member.user.is_active is False
    assert b"F002" not in admin_client.get("/faculty/").content


def test_students_cannot_manage_faculty(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="student1"))
    assert client.get("/faculty/").status_code == 403


def test_admin_dashboard_links_to_students_and_faculty(admin_client):
    response = admin_client.get("/dashboard/admin/")
    assert b'href="/students/"' in response.content
    assert b'href="/faculty/"' in response.content
