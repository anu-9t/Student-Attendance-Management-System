"""SAM-F-017: the threshold setting and low-attendance flags."""
import pytest
from django.core.management import call_command

from accounts.models import User
from audit.models import AuditLog
from notification.models import SystemSetting
from notification.services import get_threshold, is_below

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


@pytest.fixture
def admin_client(client, seeded):
    client.force_login(User.objects.get(username="admin"))
    return client


def test_default_threshold_is_75(seeded):
    assert get_threshold() == 75.0


def test_missing_or_broken_setting_falls_back_to_75():
    assert get_threshold() == 75.0
    SystemSetting.objects.create(key="attendance_threshold", value="lots")
    assert get_threshold() == 75.0


def test_is_below():
    assert is_below(74.9, 75)
    assert not is_below(75.0, 75)
    assert not is_below(None, 75)  # no classes yet is not a warning


def test_admin_changes_the_threshold(admin_client):
    response = admin_client.post("/notifications/threshold/", {"threshold": "80"})
    assert response.status_code == 302
    assert get_threshold() == 80.0
    entry = AuditLog.objects.get(action="Changed the attendance threshold")
    assert entry.detail == "75% -> 80%"


@pytest.mark.parametrize("value", ["-1", "101", "abc"])
def test_threshold_must_be_a_percentage(admin_client, value):
    response = admin_client.post("/notifications/threshold/", {"threshold": value})
    assert response.status_code == 200
    assert get_threshold() == 75.0


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_only_the_admin_sets_it(client, seeded, username):
    client.force_login(User.objects.get(username=username))
    assert client.post("/notifications/threshold/", {"threshold": "10"}).status_code == 403
    assert get_threshold() == 75.0


def test_admin_dashboard_links_to_the_setting(admin_client):
    assert b'href="/notifications/threshold/"' in admin_client.get("/dashboard/admin/").content
