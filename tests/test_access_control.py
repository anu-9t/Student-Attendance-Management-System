import pytest

from accounts.models import User
from accounts.signals import access_denied

pytestmark = [pytest.mark.django_db, pytest.mark.urls("tests.access_urls")]


def make_user(role):
    return User.objects.create_user(username=f"user_{role.lower()}", password="Sams@12345", role=role)


# SAM-SEC-001: nothing is visible without logging in


@pytest.mark.parametrize("path", ["/", "/test/admin-only/", "/test/faculty-only/"])
def test_logged_out_users_are_sent_to_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.url.startswith("/login/")


def test_login_and_health_pages_stay_open(client):
    assert client.get("/login/").status_code == 200
    assert client.get("/health/").status_code == 200


# SAM-SEC-002: each role only reaches its own pages


def test_admin_reaches_admin_page(client):
    client.force_login(make_user(User.Role.ADMIN))
    assert client.get("/test/admin-only/").status_code == 200


@pytest.mark.parametrize("role", [User.Role.FACULTY, User.Role.STUDENT])
def test_other_roles_are_refused_the_admin_page(client, role):
    client.force_login(make_user(role))
    response = client.get("/test/admin-only/")
    assert response.status_code == 403
    assert b"don't have access" in response.content


def test_decorator_accepts_several_roles(client):
    client.force_login(make_user(User.Role.FACULTY))
    assert client.get("/test/staff-only/").status_code == 200


def test_class_based_views_are_checked_too(client):
    client.force_login(make_user(User.Role.STUDENT))
    assert client.get("/test/faculty-only/").status_code == 403


def test_refusals_are_announced_for_the_audit_log(client):
    received = []

    def listener(sender, **kwargs):
        received.append(kwargs)

    access_denied.connect(listener)
    try:
        student = make_user(User.Role.STUDENT)
        client.force_login(student)
        client.get("/test/admin-only/")
    finally:
        access_denied.disconnect(listener)

    assert len(received) == 1
    assert received[0]["user"] == student
    assert received[0]["path"] == "/test/admin-only/"
