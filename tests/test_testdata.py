"""The shared test data set builds what tests/testdata.py promises."""
import pytest

from attendance.models import Attendance
from calculation.services import student_summary
from students.models import Student
from tests.testdata import DAYS, EXPECTED, term_data

pytestmark = pytest.mark.django_db


def test_term_data_gives_the_documented_percentages():
    expected = term_data()
    for srn, per_subject in expected.items():
        rows = {r.subject.code: r.percent for r in student_summary(Student.objects.get(srn=srn))}
        for code, pct in per_subject.items():
            assert rows[code] == pct, (srn, code)


def test_term_data_is_ten_days_of_two_subjects_for_four_students():
    term_data()
    assert Attendance.objects.count() == 4 * 2 * len(DAYS)
    assert all(d.weekday() < 5 for d in DAYS)
    assert EXPECTED["PES2UG24CS093"] == {"UE24CS341A": 70.0, "UE24CS342A": 70.0}
