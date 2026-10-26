"""Audit Module (SAM-SEC-005): refusals and failed logins are recorded."""
import pytest
from django.core.management import call_command

from accounts.models import User
from audit.models import AuditLog

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def seeded():
    call_command("seed_data")


def test_failed_login_is_recorded(client, seeded):
    client.post("/login/", {"username": "student1", "password": "wrong"})
    entry = AuditLog.objects.get(action="Failed login")
    assert entry.outcome == AuditLog.Outcome.FAILED
    assert "username=student1" in entry.detail
    assert entry.user is None


def test_good_login_writes_no_failure(client, seeded):
    client.post("/login/", {"username": "student1", "password": PASSWORD})
    assert not AuditLog.objects.filter(outcome=AuditLog.Outcome.FAILED).exists()


def test_refused_management_page_is_recorded(client, seeded):
    student = User.objects.get(username="student1")
    client.force_login(student)
    assert client.get("/students/").status_code == 403
    entry = AuditLog.objects.get(outcome=AuditLog.Outcome.DENIED)
    assert entry.user == student
    assert entry.detail == "/students/"


def test_entries_cannot_be_edited_or_deleted(seeded):
    entry = AuditLog.objects.create(action="x", outcome=AuditLog.Outcome.SUCCESS)
    entry.action = "changed"
    with pytest.raises(PermissionError):
        entry.save()
    with pytest.raises(PermissionError):
        entry.delete()


# UC-05: the administrator's changes are recorded


@pytest.fixture
def admin_client(client, seeded):
    client.force_login(User.objects.get(username="admin"))
    return client


def test_adding_a_student_is_recorded(admin_client):
    from students.models import ClassGroup

    group = ClassGroup.objects.get(name="CSE-5A")
    admin_client.post(
        "/students/add/",
        {"srn": "PES2UG24CS150", "name": "Audit Test", "email": "", "class_group": group.id, "password": "Welcome@123"},
    )
    entry = AuditLog.objects.get(action="Added a student")
    assert entry.user.username == "admin"
    assert entry.target_type == "Student"
    assert entry.detail == "PES2UG24CS150"


def test_deactivating_faculty_is_recorded(admin_client):
    from faculty.models import Faculty

    member = Faculty.objects.get(user__username="faculty2")
    admin_client.post(f"/faculty/{member.pk}/deactivate/")
    entry = AuditLog.objects.get(action="Deactivated a faculty member")
    assert entry.target_id == str(member.pk)


def test_editing_a_subject_records_what_changed(admin_client):
    from subjects.models import Subject

    subject = Subject.objects.order_by("code").first()
    admin_client.post(f"/subjects/{subject.pk}/edit/", {"code": subject.code, "name": "Renamed", "semester": subject.semester})
    entry = AuditLog.objects.get(action="Updated a subject")
    assert entry.detail == "name"


def test_a_refused_change_writes_no_success_entry(client, seeded):
    client.force_login(User.objects.get(username="faculty1"))
    client.post("/subjects/add/", {"code": "X1", "name": "X", "semester": 5})
    assert not AuditLog.objects.filter(outcome=AuditLog.Outcome.SUCCESS).exists()


# The audit log page


def test_admin_reads_the_log_newest_first(admin_client):
    AuditLog.objects.create(action="First thing", outcome=AuditLog.Outcome.SUCCESS)
    AuditLog.objects.create(action="Second thing", outcome=AuditLog.Outcome.SUCCESS)
    response = admin_client.get("/audit/")
    assert response.status_code == 200
    body = response.content.decode()
    assert body.index("Second thing") < body.index("First thing")


def test_log_can_be_filtered_by_outcome(admin_client):
    AuditLog.objects.create(action="Kept", outcome=AuditLog.Outcome.DENIED)
    AuditLog.objects.create(action="Hidden", outcome=AuditLog.Outcome.SUCCESS)
    body = admin_client.get("/audit/?outcome=DENIED").content.decode()
    assert "Kept" in body and "Hidden" not in body


def test_log_can_be_searched(admin_client):
    AuditLog.objects.create(action="Added a student", detail="PES2UG24CS777", outcome=AuditLog.Outcome.SUCCESS)
    AuditLog.objects.create(action="Added a subject", detail="CS999", outcome=AuditLog.Outcome.SUCCESS)
    body = admin_client.get("/audit/?q=CS777").content.decode()
    assert "PES2UG24CS777" in body and "CS999" not in body


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_only_the_admin_reads_the_log(client, seeded, username):
    client.force_login(User.objects.get(username=username))
    assert client.get("/audit/").status_code == 403


def test_admin_dashboard_links_to_the_log(admin_client):
    assert b'href="/audit/"' in admin_client.get("/dashboard/admin/").content
