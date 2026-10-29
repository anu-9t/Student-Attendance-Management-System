"""TC-Perf-01 (SAM-NF-001): pages answer within 3 seconds with a term's worth of data.

Owner: Anmol Vyas. The database gets seed_data plus seed_load (2 classes x 60 students x
20 days, about 7,500 attendance rows on top of the sample set), then every main page is
timed for the role that uses it. The limit is the SRS's 3 seconds; the test prints each time
so the numbers can go in the test summary (docs/testing/test-summary.md).
"""
import time

import pytest
from django.core.management import call_command

from accounts.models import User
from students.models import ClassGroup, Student
from subjects.models import Subject

pytestmark = pytest.mark.django_db

LIMIT_SECONDS = 3.0


@pytest.fixture
def loaded():
    call_command("seed_data", verbosity=0)
    call_command("seed_load", classes=2, students=60, days=20, verbosity=0)


def timed_get(client, url, **params):
    start = time.perf_counter()
    response = client.get(url, params)
    return response, time.perf_counter() - start


def pages(role):
    group = ClassGroup.objects.get(name="LOAD-1")
    subject = Subject.objects.get(code="UE24CS341A")
    student = Student.objects.filter(class_group=group).first()
    if role == "admin":
        return [
            "/dashboard/admin/", "/students/", "/reports/", f"/reports/class/{group.pk}/",
            f"/reports/subject/{group.pk}/{subject.pk}/", f"/reports/student/{student.pk}/",
            f"/history/student/{student.pk}/", "/audit/",
        ]
    if role == "faculty1":
        return ["/dashboard/faculty/", "/attendance/select/", f"/attendance/mark/{group.pk}/{subject.pk}/",
                f"/attendance/modify/{group.pk}/{subject.pk}/", f"/reports/subject/{group.pk}/{subject.pk}/"]
    return ["/dashboard/student/", "/percentage/", "/history/"]


@pytest.mark.parametrize("username", ["admin", "faculty1", "student1"])
def test_tc_perf_01_every_page_answers_within_3_seconds(client, loaded, username):
    client.force_login(User.objects.get(username=username))
    times = []
    for url in pages(username):
        response, seconds = timed_get(client, url)
        assert response.status_code == 200, url
        times.append((seconds, url))
    for seconds, url in sorted(times, reverse=True):
        print(f"TC-Perf-01 {username:9} {seconds * 1000:7.1f} ms  {url}")
    slowest, url = max(times)
    assert slowest < LIMIT_SECONDS, f"{url} took {slowest:.2f}s"


def test_tc_perf_01_downloads_within_3_seconds(client, loaded):
    client.force_login(User.objects.get(username="admin"))
    group = ClassGroup.objects.get(name="LOAD-1")
    for fmt in ("csv", "pdf"):
        response, seconds = timed_get(client, f"/reports/class/{group.pk}/", format=fmt)
        assert response.status_code == 200
        print(f"TC-Perf-01 download {fmt}: {seconds * 1000:.1f} ms")
        assert seconds < LIMIT_SECONDS


def test_tc_perf_01_saving_a_full_sheet_within_3_seconds(client, loaded):
    from subjects.models import SubjectAssignment, TimeSlot

    client.force_login(User.objects.get(username="faculty1"))
    a = SubjectAssignment.objects.filter(faculty__user__username="faculty1", class_group__name="LOAD-2").first()
    data = {"date": "2026-10-29", "slots": [TimeSlot.objects.get(label="Period 6").pk]}
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        data[f"status_{s.pk}"] = "PRESENT"
    start = time.perf_counter()
    response = client.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", data)
    seconds = time.perf_counter() - start
    print(f"TC-Perf-01 save 60-student sheet: {seconds * 1000:.1f} ms")
    assert response.status_code == 302
    assert seconds < LIMIT_SECONDS
