import pytest

from accounts.models import User

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


@pytest.fixture
def faculty_user():
    return User.objects.create_user(username="faculty1", password=PASSWORD, role=User.Role.FACULTY)


def test_login_page_loads(client):
    response = client.get("/login/")
    assert response.status_code == 200
    assert b"Log in" in response.content


def test_correct_login_is_accepted(client, faculty_user):
    response = client.post("/login/", {"username": "faculty1", "password": PASSWORD})
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


def test_logout_ends_the_session(client, faculty_user):
    client.force_login(faculty_user)
    response = client.post("/logout/")
    assert response.status_code == 302
    assert response.url == "/login/"
    assert "_auth_user_id" not in client.session


# SAM-F-002: wrong details are rejected with a clear message


def test_wrong_password_shows_an_error(client, faculty_user):
    response = client.post("/login/", {"username": "faculty1", "password": "not-the-password"})
    assert response.status_code == 200
    assert b"Wrong username or password" in response.content
    assert "_auth_user_id" not in client.session


def test_unknown_username_shows_the_same_error(client):
    response = client.post("/login/", {"username": "nobody", "password": PASSWORD})
    assert b"Wrong username or password" in response.content


def test_deactivated_user_cannot_log_in(client, faculty_user):
    faculty_user.is_active = False
    faculty_user.save()
    client.post("/login/", {"username": "faculty1", "password": PASSWORD})
    assert "_auth_user_id" not in client.session


# SAM-F-003: each role is sent to its own dashboard


@pytest.mark.parametrize(
    "role, expected",
    [
        (User.Role.ADMIN, "/dashboard/admin/"),
        (User.Role.FACULTY, "/dashboard/faculty/"),
        (User.Role.STUDENT, "/dashboard/student/"),
    ],
)
def test_each_role_lands_on_its_own_dashboard(client, role, expected):
    User.objects.create_user(username="someone", password=PASSWORD, role=role)
    client.post("/login/", {"username": "someone", "password": PASSWORD})
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == expected
