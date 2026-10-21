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
