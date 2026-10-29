"""TC-Reliability-01 (SAM-NF-002): the system fails safely and keeps serving.

Owner: Anupriya. Checks:
- the health check notices a lost database (503), so Docker restarts the container;
- one failing request doesn't affect the next one;
- users get a plain error page, never a stack trace, when DEBUG is off;
- a save that fails half-way leaves nothing behind (all or nothing);
- the restart policies and health checks are in place (tests/test_availability.py covers the file).
"""
import pytest
from django.core.management import call_command
from django.db import DatabaseError, IntegrityError
from django.test import Client, override_settings
from django.urls import path

from accounts.models import User

pytestmark = pytest.mark.django_db


def broken_view(request):
    raise RuntimeError("simulated failure")


urlpatterns = [path("", __import__("django").urls.include("sams.urls")), path("test/broken/", broken_view)]


def test_tc_reliability_01a_health_is_ok_when_the_database_answers(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tc_reliability_01b_health_reports_a_lost_database(client, monkeypatch):
    import sams.urls

    class DeadCursor:
        def __enter__(self):
            raise DatabaseError("server has gone away")

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(sams.urls.connection, "cursor", lambda: DeadCursor())
    response = client.get("/health/")
    assert response.status_code == 503
    assert response.json()["status"] == "error"


@pytest.mark.urls(__name__)
@override_settings(DEBUG=False)
def test_tc_reliability_01c_a_crash_shows_a_plain_page_and_the_next_request_works():
    call_command("seed_data", verbosity=0)
    client = Client(raise_request_exception=False)
    client.force_login(User.objects.get(username="admin"))
    crashed = client.get("/test/broken/")
    assert crashed.status_code == 500
    assert b"Something went wrong on our side" in crashed.content
    assert b"Traceback" not in crashed.content and b"simulated failure" not in crashed.content
    assert client.get("/dashboard/admin/").status_code == 200


@override_settings(DEBUG=False)
def test_tc_reliability_01d_unknown_pages_get_a_plain_404(client):
    call_command("seed_data", verbosity=0)
    client.force_login(User.objects.get(username="student1"))
    response = client.get("/no/such/page/")
    assert response.status_code == 404
    assert b"We couldn't find that page" in response.content


def test_tc_reliability_01e_a_failed_save_leaves_nothing_behind(client, monkeypatch):
    from attendance.models import Attendance
    from students.models import Student
    from subjects.models import SubjectAssignment, TimeSlot

    call_command("seed_data", verbosity=0)
    client.force_login(User.objects.get(username="faculty1"))
    a = SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()
    data = {"date": "2026-10-29", "slots": [TimeSlot.objects.get(label="Period 2").pk]}
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        data[f"status_{s.pk}"] = "PRESENT"

    def fail(*args, **kwargs):
        raise IntegrityError("simulated clash")

    monkeypatch.setattr(Attendance.objects, "bulk_create", fail)
    response = client.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", data)
    assert response.status_code == 200
    assert b"Nothing was saved" in response.content
    assert Attendance.objects.count() == 0
