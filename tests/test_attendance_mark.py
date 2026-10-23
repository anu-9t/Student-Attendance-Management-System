import pytest
from django.core.management import call_command

from accounts.models import User
from students.models import Student
from subjects.models import SubjectAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def faculty_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    return client


def own_assignment():
    return SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()


# SAM-F-011: the marking sheet


def test_marking_sheet_lists_the_active_students_of_the_class(faculty_client):
    a = own_assignment()
    Student.objects.filter(srn="PES2UG24CS092").update(is_active=False)  # in CSE-5A, deactivated
    response = faculty_client.get(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/")
    assert response.status_code == 200
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        assert s.srn.encode() in response.content
    assert b"PES2UG24CS092" not in response.content
    assert b"Period 1" in response.content


def test_selected_pair_links_to_the_marking_sheet(faculty_client):
    a = own_assignment()
    response = faculty_client.get("/attendance/select/", {"class_id": a.class_group_id, "subject_id": a.subject_id})
    assert f"/attendance/mark/{a.class_group_id}/{a.subject_id}/".encode() in response.content


def test_marking_sheet_for_someone_elses_class_is_refused(faculty_client):
    other = SubjectAssignment.objects.exclude(faculty__user__username="faculty1").first()
    assert faculty_client.get(f"/attendance/mark/{other.class_group_id}/{other.subject_id}/").status_code == 404
