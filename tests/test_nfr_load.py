"""TC-Load-01 (SAM-NF-007): many users at once, with no errors and no slow pages.

Owner: Anupriya. With load data in the database, 20 users (8 students, 4 faculty sessions,
the admin and more) work at the same time from 20 threads, 200 page views in total. Every
request must succeed and 95% must answer within the 3-second limit of SAM-NF-001.

Sessions are kept in signed cookies for this test only, so the 20 threads don't queue on the
session table of the test database; that table isn't part of what's being measured.

The 20 threads share one Python process here, so each request waits its turn for the
interpreter and the times are pessimistic. The real server runs several gunicorn workers.
"""
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.core.management import call_command
from django.db import connections
from django.test import Client

from accounts.models import User
from students.models import ClassGroup
from subjects.models import Subject

pytestmark = pytest.mark.django_db(transaction=True)

USERS = 20
VIEWS_PER_USER = 10
LIMIT_SECONDS = 3.0


@pytest.fixture
def loaded(settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    call_command("seed_data", verbosity=0)
    call_command("seed_load", classes=2, students=30, days=10, verbosity=0)


def journeys():
    """(user, pages) for each simulated user: students, both faculty members and the admin."""
    group = ClassGroup.objects.get(name="LOAD-1")
    taught = {"faculty1": Subject.objects.get(code="UE24CS341A"), "faculty2": Subject.objects.get(code="UE24CS342A")}
    student_pages = ["/dashboard/student/", "/percentage/", "/history/"]
    admin_pages = ["/dashboard/admin/", f"/reports/class/{group.pk}/", "/students/", "/audit/"]
    usernames = [f"student{i}" for i in range(1, 9)] + ["faculty1", "faculty2"] * 4 + ["admin"] * 4
    plan = []
    for username in usernames[:USERS]:
        if username.startswith("student"):
            pages = student_pages
        elif username in taught:
            pages = ["/dashboard/faculty/", "/attendance/select/", f"/reports/subject/{group.pk}/{taught[username].pk}/"]
        else:
            pages = admin_pages
        plan.append((User.objects.get(username=username), [pages[i % len(pages)] for i in range(VIEWS_PER_USER)]))
    return plan


def run_user(client, urls, start_gate):
    """One user's visit: wait for everyone, then open the pages one after another."""
    results = []
    start_gate.wait(timeout=60)
    try:
        for url in urls:
            began = time.perf_counter()
            status = client.get(url).status_code
            results.append((status, time.perf_counter() - began, url))
    finally:
        connections.close_all()
    return results


def test_tc_load_01_twenty_users_at_once(loaded):
    plan = []
    for user, urls in journeys():
        client = Client()
        client.force_login(user)  # logging in happens before the clock starts
        plan.append((client, urls))
    gate = threading.Barrier(len(plan))
    began = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(plan)) as pool:
        futures = [pool.submit(run_user, client, urls, gate) for client, urls in plan]
        results = [r for f in futures for r in f.result(timeout=120)]
    wall = time.perf_counter() - began

    times = sorted(t for _, t, _ in results)
    p95 = times[int(len(times) * 0.95) - 1]
    errors = [(s, u) for s, _, u in results if s != 200]
    print(f"TC-Load-01 {len(results)} requests from {len(plan)} users in {wall:.2f}s: "
          f"median {statistics.median(times) * 1000:.0f} ms, 95th percentile {p95 * 1000:.0f} ms, "
          f"slowest {times[-1] * 1000:.0f} ms, errors {len(errors)}")
    assert len(results) == USERS * VIEWS_PER_USER
    assert not errors, errors[:5]
    assert p95 < LIMIT_SECONDS
