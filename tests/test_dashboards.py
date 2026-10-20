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
