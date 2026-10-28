"""SAM-F-020: report downloads (CSV, PDF) and printing."""
import csv
import datetime as dt
import io

import pytest
from django.core.management import call_command

from accounts.models import User
from attendance.models import Attendance
from faculty.models import Faculty
from reports.export import _safe
from students.models import ClassGroup, Student
from subjects.models import Subject, TimeSlot

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="admin"))
    return client


def class_url():
    return f"/reports/class/{ClassGroup.objects.get(name='CSE-5A').pk}/"


def mark(srn, day, status):
    Attendance.objects.create(
        student=Student.objects.get(srn=srn),
        subject=Subject.objects.get(code="UE24CS341A"),
        date=dt.date(2026, 10, day),
        time_slot=TimeSlot.objects.get(label="Period 1"),
        status=status,
        marked_by=Faculty.objects.first(),
    )


def read_csv(response):
    return list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))


def test_csv_download_has_the_same_numbers_as_the_page(admin_client):
    mark("PES2UG24CS091", 20, "PRESENT")
    mark("PES2UG24CS091", 21, "ABSENT")
    response = admin_client.get(class_url(), {"format": "csv"})
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment;" in response["Content-Disposition"]
    rows = read_csv(response)
    assert rows[0] == ["CSE-5A class-wise report"]
    header = rows[3]
    assert header[:2] == ["SRN", "Name"] and header[-1] == "Overall"
    row = next(r for r in rows if r and r[0] == "PES2UG24CS091")
    assert row[header.index("UE24CS341A")] == "50.0%"


def test_csv_keeps_the_date_range(admin_client):
    mark("PES2UG24CS091", 20, "PRESENT")
    mark("PES2UG24CS091", 27, "ABSENT")
    rows = read_csv(admin_client.get(class_url(), {"format": "csv", "date_from": "2026-10-25"}))
    assert "from 25 Oct 2026" in rows[1][0]
    row = next(r for r in rows if r and r[0] == "PES2UG24CS091")
    assert "0.0%" in row


def test_report_page_offers_the_download(admin_client):
    assert b"format=csv" in admin_client.get(class_url()).content


def test_cells_that_look_like_formulas_are_neutralised():
    assert _safe("=HYPERLINK(1)") == "'=HYPERLINK(1)"
    assert _safe("-") == "-"
    assert _safe(5) == 5


def test_faculty_cannot_download_a_class_they_dont_teach(client):
    call_command("seed_data")
    other = ClassGroup.objects.create(name="ME-3A", department="ME", semester=3)
    client.force_login(User.objects.get(username="faculty1"))
    assert client.get(f"/reports/class/{other.pk}/", {"format": "csv"}).status_code == 403
