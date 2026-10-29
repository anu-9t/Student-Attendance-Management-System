"""The shared test data set for the use-case tests (STP Section 6, test data).

term_data() builds on seed_data and marks UE24CS341A and UE24CS342A for class CSE-5A over
ten teaching days (1-14 Oct 2026, one Period 1 class of UE24CS341A and one Period 3 class of
UE24CS342A a day), so each student ends up with a known percentage:

    SRN            UE24CS341A        UE24CS342A        Why this student is in the set
    PES2UG24CS091  10/10 = 100.0%    10/10 = 100.0%    never absent
    PES2UG24CS092   5/10 =  50.0%     8/10 =  80.0%    low in one subject only
    PES2UG24CS093   7/10 =  70.0%     7/10 =  70.0%    just under the 75% threshold in both
    PES2UG24CS094   8/10 =  80.0%     6/10 =  60.0%    above in one, below in the other

docs/testing/test-data.md describes the same set for manual testing.
"""
import datetime as dt

from django.core.management import call_command

from attendance.models import Attendance
from faculty.models import Faculty
from students.models import Student
from subjects.models import Subject, TimeSlot

DAYS = [dt.date(2026, 10, d) for d in (1, 2, 5, 6, 7, 8, 9, 12, 13, 14)]  # ten weekdays

# SRN -> how many of the ten classes they attended, per subject
ATTENDED = {
    "PES2UG24CS091": {"UE24CS341A": 10, "UE24CS342A": 10},
    "PES2UG24CS092": {"UE24CS341A": 5, "UE24CS342A": 8},
    "PES2UG24CS093": {"UE24CS341A": 7, "UE24CS342A": 7},
    "PES2UG24CS094": {"UE24CS341A": 8, "UE24CS342A": 6},
}
SLOTS = {"UE24CS341A": "Period 1", "UE24CS342A": "Period 3"}
EXPECTED = {
    srn: {code: round(n * 100 / len(DAYS), 1) for code, n in per_subject.items()}
    for srn, per_subject in ATTENDED.items()
}


def term_data():
    """Seed the sample data and the attendance above. Returns the EXPECTED percentages."""
    call_command("seed_data", verbosity=0)
    markers = {
        "UE24CS341A": Faculty.objects.get(employee_id="F001"),
        "UE24CS342A": Faculty.objects.get(employee_id="F002"),
    }
    rows = []
    for srn, per_subject in ATTENDED.items():
        student = Student.objects.get(srn=srn)
        for code, attended in per_subject.items():
            subject = Subject.objects.get(code=code)
            slot = TimeSlot.objects.get(label=SLOTS[code])
            for i, day in enumerate(DAYS):
                status = Attendance.Status.PRESENT if i < attended else Attendance.Status.ABSENT
                rows.append(Attendance(student=student, subject=subject, date=day, time_slot=slot,
                                       status=status, marked_by=markers[code]))
    Attendance.objects.bulk_create(rows)
    return EXPECTED
