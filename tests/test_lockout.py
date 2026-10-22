import pytest

from accounts.models import User

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def student():
    return User.objects.create_user(username="student1", password=PASSWORD, role=User.Role.STUDENT)


def fail_login(client, times, ip="10.0.0.1"):
    response = None
    for _ in range(times):
        response = client.post(
            "/login/", {"username": "student1", "password": "wrong"}, REMOTE_ADDR=ip
        )
    return response


# SAM-SEC-003: lockout after repeated failures


def test_four_failures_do_not_lock_the_account(client, student):
    fail_login(client, 4)
    response = client.post("/login/", {"username": "student1", "password": PASSWORD}, REMOTE_ADDR="10.0.0.1")
    assert response.status_code == 302


def test_fifth_failure_locks_the_account_with_429(client, student):
    response = fail_login(client, 5)
    assert response.status_code == 429
    assert b"Too many failed login attempts" in response.content


def test_locked_account_refuses_even_the_right_password(client, student):
    fail_login(client, 5)
    response = client.post("/login/", {"username": "student1", "password": PASSWORD}, REMOTE_ADDR="10.0.0.1")
    assert response.status_code == 429
    assert "_auth_user_id" not in client.session


def test_lockout_is_per_device(client, student):
    fail_login(client, 5, ip="10.0.0.1")
    response = client.post("/login/", {"username": "student1", "password": PASSWORD}, REMOTE_ADDR="10.0.0.2")
    assert response.status_code == 302


# SAM-SEC-003: passwords are stored hashed, never as plain text


def test_password_is_stored_hashed(student):
    student.refresh_from_db()
    assert student.password != PASSWORD
    assert student.password.startswith("pbkdf2_sha256$")
    assert student.check_password(PASSWORD)
