"""Test cases for UC-03 (View Attendance Percentage) and UC-07 (View Attendance History).

TC-Calc-01 (SAM-F-015), TC-Alert-01 (SAM-F-017), TC-View-01 (SAM-F-016), TC-SEC-04 (SAM-SEC-004).
Test owner: Anusha G (STP Section 9). Data: tests/testdata.py (docs/testing/test-data.md).
Students log in through the real login page.
"""
import pytest

from students.models import Student
from tests.testdata import DAYS, EXPECTED, term_data

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"
LOGIN = {"PES2UG24CS091": "student1", "PES2UG24CS092": "student2",
         "PES2UG24CS093": "student3", "PES2UG24CS094": "student4"}


@pytest.fixture
def term():
    return term_data()


def login(client, username):
    client.post("/logout/")
    assert client.post("/login/", {"username": username, "password": PASSWORD}).status_code == 302


# UC-03 / TC-Calc-01: the percentage per subject


@pytest.mark.parametrize("srn", list(EXPECTED))
def test_tc_calc_01_each_student_sees_the_expected_percentages(client, term, srn):
    login(client, LOGIN[srn])
    body = client.get("/percentage/").content.decode()
    for pct in EXPECTED[srn].values():
        assert f"{pct}%" in body


def test_tc_calc_01b_overall_line(client, term):
    login(client, "student2")  # 5 + 8 of 20
    body = client.get("/percentage/").content.decode()
    assert "65.0%" in body


def test_tc_calc_01c_held_classes_count_every_slot(client, term):
    login(client, "student1")
    body = client.get("/percentage/").content.decode()
    assert f"<td class=\"text-end\">{len(DAYS)}</td>" in body


# UC-03 / TC-Alert-01: low-attendance flags


def test_tc_alert_01a_no_warning_for_a_full_record(client, term):
    login(client, "student1")
    assert b"Low attendance" not in client.get("/dashboard/student/").content


def test_tc_alert_01b_warning_names_only_the_low_subject(client, term):
    login(client, "student2")
    body = client.get("/dashboard/student/").content.decode()
    assert "UE24CS341A (50.0%)" in body
    assert "UE24CS342A (" not in body


def test_tc_alert_01c_just_under_the_threshold_is_flagged(client, term):
    login(client, "student3")
    body = client.get("/dashboard/student/").content.decode()
    assert "UE24CS341A (70.0%)" in body and "UE24CS342A (70.0%)" in body


def test_tc_alert_01d_faculty_see_their_low_students(client, term):
    login(client, "faculty1")  # teaches UE24CS341A: 092 at 50% and 093 at 70% are low, 094 at 80% isn't
    body = client.get("/dashboard/faculty/").content.decode()
    flagged = body[body.index("Students below"): body.index('<div class="row g-4')]
    names = {srn: Student.objects.get(srn=srn).name for srn in EXPECTED}
    assert names["PES2UG24CS092"] in flagged and names["PES2UG24CS093"] in flagged
    assert names["PES2UG24CS091"] not in flagged and names["PES2UG24CS094"] not in flagged


def test_tc_alert_01e_admin_raises_the_threshold_and_more_are_flagged(client, term):
    login(client, "admin")
    client.post("/notifications/threshold/", {"threshold": "85"})
    login(client, "student2")  # 80% in UE24CS342A is now low too
    assert b"UE24CS342A (80.0%)" in client.get("/dashboard/student/").content


# UC-07 / TC-View-01: history, newest first


def test_tc_view_01a_history_lists_every_class_newest_first(client, term):
    login(client, "student2")
    body = client.get("/history/").content.decode()
    assert body.index("Wed 14 Oct 2026") < body.index("Thu 01 Oct 2026")
    assert "Page 1 of 1" not in body  # 20 classes fit on one page


def test_tc_view_01b_absences_are_shown(client, term):
    login(client, "student2")
    body = client.get("/history/").content.decode()
    assert body.count("bg-danger") == 5 + 2  # 5 absences in UE24CS341A, 2 in UE24CS342A


def test_tc_view_01c_filter_by_subject(client, term):
    from subjects.models import Subject

    login(client, "student2")
    body = client.get("/history/", {"subject": Subject.objects.get(code="UE24CS342A").pk}).content.decode()
    assert "UE24CS341A" not in body.split("<tbody>")[1]


# UC-07 / TC-SEC-04: a student only ever sees their own records


def test_tc_sec_04a_student_cannot_open_another_students_history(client, term):
    login(client, "student1")
    other = Student.objects.get(srn="PES2UG24CS092")
    assert client.get(f"/history/student/{other.pk}/").status_code == 403


def test_tc_sec_04b_student_cannot_open_reports(client, term):
    login(client, "student1")
    other = Student.objects.get(srn="PES2UG24CS092")
    assert client.get(f"/reports/student/{other.pk}/").status_code == 403


def test_tc_sec_04c_pages_never_show_another_students_srn(client, term):
    login(client, "student1")
    for url in ["/dashboard/student/", "/percentage/", "/history/"]:
        assert b"PES2UG24CS092" not in client.get(url).content, url


def test_tc_sec_04d_refusals_are_audited(client, term):
    from audit.models import AuditLog

    login(client, "student1")
    other = Student.objects.get(srn="PES2UG24CS092")
    client.get(f"/history/student/{other.pk}/")
    assert AuditLog.objects.filter(outcome="DENIED", user__username="student1").exists()
