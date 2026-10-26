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
