import pytest
from django.core.management import call_command

from accounts.models import User
from subjects.models import SubjectAssignment

pytestmark = pytest.mark.django_db


# SAM-F-010: faculty select a class and subject they are assigned to


def test_faculty_can_view_and_select_only_assigned_pairs(client):
    call_command("seed_data")
    faculty_user = User.objects.get(username="faculty1")
    assignment = SubjectAssignment.objects.filter(faculty__user=faculty_user).first()
    client.force_login(faculty_user)

    response = client.get("/attendance/select/")
    assert response.status_code == 200
    assert assignment.class_group.name.encode() in response.content
    assert assignment.subject.code.encode() in response.content

    response = client.get(
        "/attendance/select/",
        {"class_id": assignment.class_group_id, "subject_id": assignment.subject_id},
    )
    assert response.status_code == 200
    assert b"Selected:" in response.content


def test_a_pair_not_assigned_to_you_is_refused(client):
    call_command("seed_data")
    faculty_user = User.objects.get(username="faculty1")
    other = SubjectAssignment.objects.exclude(faculty__user=faculty_user).first()
    client.force_login(faculty_user)
    response = client.get("/attendance/select/", {"class_id": other.class_group_id, "subject_id": other.subject_id})
    assert response.status_code == 404


def test_faculty_assignment_page_rejects_other_roles(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="admin"))
    assert client.get("/attendance/select/").status_code == 403


def test_faculty_dashboard_links_to_attendance(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    assert b'href="/attendance/select/"' in client.get("/dashboard/faculty/").content
