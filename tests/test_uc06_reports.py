"""Test cases for UC-06 (Generate Reports): TC-Report-01 to TC-Report-03.

Test owner: Anmol Vyas (STP Section 13). The data is marked through the real marking page,
then the reports are opened and downloaded as a faculty member and as the admin would.
"""
import csv
import io

import pytest
from django.core.management import call_command

from students.models import ClassGroup, Student
from subjects.models import Subject, SubjectAssignment, TimeSlot

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


def login(client, username):
    client.post("/logout/")
    assert client.post("/login/", {"username": username, "password": PASSWORD}).status_code == 302


@pytest.fixture
def marked(client):
    """faculty1 marks UE24CS341A for CSE-5A on three days; PES2UG24CS092 misses two of them."""
    call_command("seed_data")
    login(client, "faculty1")
    a = SubjectAssignment.objects.get(faculty__user__username="faculty1", class_group__name="CSE-5A")
    slot = TimeSlot.objects.get(label="Period 1")
    for day, absent in [("2026-10-20", {"PES2UG24CS092"}), ("2026-10-21", {"PES2UG24CS092"}), ("2026-10-22", set())]:
        data = {"date": day, "slots": [slot.pk]}
        for s in Student.objects.filter(class_group=a.class_group, is_active=True):
            data[f"status_{s.pk}"] = "ABSENT" if s.srn in absent else "PRESENT"
        assert client.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", data).status_code == 302
    return client


def cse5a():
    return ClassGroup.objects.get(name="CSE-5A")


def se():
    return Subject.objects.get(code="UE24CS341A")


def row_for(body, srn):
    """The text of the table row for one SRN."""
    start = body.index(srn)
    return body[start: body.index("</tr>", start)]


# TC-Report-01: student-wise report (SAM-F-018)


def test_tc_report_01a_student_wise_report_shows_each_subject(marked):
    student = Student.objects.get(srn="PES2UG24CS092")
    body = marked.get(f"/reports/student/{student.pk}/").content.decode()
    assert "UE24CS341A" in body
    assert "33.3%" in body  # 1 of 3


def test_tc_report_01b_admin_sees_every_subject_of_the_student(marked):
    login(marked, "admin")
    student = Student.objects.get(srn="PES2UG24CS092")
    body = marked.get(f"/reports/student/{student.pk}/").content.decode()
    assert "UE24CS341A" in body and "UE24CS342A" in body


# TC-Report-02: subject-wise and class-wise reports (SAM-F-019)


def test_tc_report_02a_subject_wise_numbers(marked):
    body = marked.get(f"/reports/subject/{cse5a().pk}/{se().pk}/").content.decode()
    assert "100.0%" in row_for(body, "PES2UG24CS091")
    assert "33.3%" in row_for(body, "PES2UG24CS092")


def test_tc_report_02b_class_wise_overall_column(marked):
    login(marked, "admin")
    body = marked.get(f"/reports/class/{cse5a().pk}/").content.decode()
    row = row_for(body, "PES2UG24CS092")
    assert "33.3%" in row  # UE24CS341A and overall; nothing marked in UE24CS342A yet
    assert "-" in row


def test_tc_report_02c_date_range(marked):
    body = marked.get(
        f"/reports/subject/{cse5a().pk}/{se().pk}/", {"date_from": "2026-10-22", "date_to": "2026-10-22"}
    ).content.decode()
    assert "100.0%" in row_for(body, "PES2UG24CS092")


def test_tc_report_02d_faculty_cannot_report_on_other_subjects(marked):
    cn = Subject.objects.get(code="UE24CS342A")
    assert marked.get(f"/reports/subject/{cse5a().pk}/{cn.pk}/").status_code == 403


def test_tc_report_02e_students_get_no_reports(marked):
    login(marked, "student1")
    assert marked.get("/reports/").status_code == 403


# TC-Report-03: download and print (SAM-F-020)


def test_tc_report_03a_csv_matches_the_page(marked):
    response = marked.get(f"/reports/subject/{cse5a().pk}/{se().pk}/", {"format": "csv"})
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    row = next(r for r in rows if r and r[0] == "PES2UG24CS092")
    assert row[2:] == ["1", "3", "33.3%"]


def test_tc_report_03b_pdf_downloads(marked):
    response = marked.get(f"/reports/subject/{cse5a().pk}/{se().pk}/", {"format": "pdf"})
    assert response["Content-Type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_tc_report_03c_print_button(marked):
    assert b"window.print()" in marked.get(f"/reports/class/{cse5a().pk}/").content
