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
