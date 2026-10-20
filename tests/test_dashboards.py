import pytest
from django.urls import reverse

from accounts.models import User


@pytest.mark.django_db
def test_admin_dashboard(client):
    user = User.objects.create_user(
        username="test_admin",
        password="TestPass@123",
        role="ADMIN",
    )

    client.force_login(user)

    response = client.get(reverse("dashboards:home"))

    assert response.status_code == 200
    assert b"Administrator Dashboard" in response.content


@pytest.mark.django_db
def test_faculty_dashboard(client):
    user = User.objects.create_user(
        username="test_faculty",
        password="TestPass@123",
        role="FACULTY",
    )

    client.force_login(user)

    response = client.get(reverse("dashboards:home"))

    assert response.status_code == 200
    assert b"Faculty Dashboard" in response.content


@pytest.mark.django_db
def test_student_dashboard(client):
    user = User.objects.create_user(
        username="test_student",
        password="TestPass@123",
        role="STUDENT",
    )

    client.force_login(user)

    response = client.get(reverse("dashboards:home"))

    assert response.status_code == 200
    assert b"Student Dashboard" in response.content


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboards:home"))

    assert response.status_code == 302
    assert response.url.startswith("/login/")


# Each role also has its own address, which login sends people to.


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role, url_name, heading",
    [
        ("ADMIN", "dashboards:admin", b"Administrator Dashboard"),
        ("FACULTY", "dashboards:faculty", b"Faculty Dashboard"),
        ("STUDENT", "dashboards:student", b"Student Dashboard"),
    ],
)
def test_each_role_has_its_own_dashboard_page(client, role, url_name, heading):
    user = User.objects.create_user(username="someone", password="TestPass@123", role=role)
    client.force_login(user)
    response = client.get(reverse(url_name))
    assert response.status_code == 200
    assert heading in response.content


@pytest.mark.django_db
def test_student_cannot_open_the_admin_dashboard(client):
    user = User.objects.create_user(username="s", password="TestPass@123", role="STUDENT")
    client.force_login(user)
    assert client.get(reverse("dashboards:admin")).status_code == 403


@pytest.mark.django_db
def test_faculty_dashboard_lists_assigned_subjects(client):
    from django.core.management import call_command

    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    response = client.get(reverse("dashboards:faculty"))
    assert b"UE24CS341A" in response.content


@pytest.mark.django_db
def test_navbar_has_a_logout_button(client):
    user = User.objects.create_user(username="nav_user", password="TestPass@123", role="ADMIN")
    client.force_login(user)
    response = client.get(reverse("dashboards:home"))
    assert b"Log out" in response.content
    assert b"nav_user" in response.content
