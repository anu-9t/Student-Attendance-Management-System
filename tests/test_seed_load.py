"""SAM-NF-007 (scalability): the load-data command used by the load and performance tests."""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from attendance.models import Attendance
from students.models import ClassGroup, Student
from subjects.models import Subject

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


def test_needs_the_sample_data_first():
    with pytest.raises(CommandError, match="seed_data"):
        call_command("seed_load", classes=1, students=2, days=1)


def test_creates_the_requested_amount(seeded):
    call_command("seed_load", classes=2, students=5, days=3)
    assert ClassGroup.objects.filter(name__startswith="LOAD-").count() == 2
    assert Student.objects.filter(srn__startswith="PES2UG24LD").count() == 10
    subjects = Subject.objects.count()
    assert Attendance.objects.filter(student__srn__startswith="PES2UG24LD").count() == 10 * subjects * 3


def test_running_twice_adds_nothing_new(seeded):
    call_command("seed_load", classes=1, students=4, days=2)
    before = Attendance.objects.count()
    call_command("seed_load", classes=1, students=4, days=2)
    assert Attendance.objects.count() == before


def test_same_data_on_every_run(seeded):
    call_command("seed_load", classes=1, students=6, days=4)
    first = sorted(Attendance.objects.values_list("student__srn", "subject__code", "date", "status"))
    call_command("seed_load", clear=True)
    call_command("seed_load", classes=1, students=6, days=4)
    assert sorted(Attendance.objects.values_list("student__srn", "subject__code", "date", "status")) == first


def test_clear_removes_only_the_load_data(seeded):
    sample_students = Student.objects.count()
    call_command("seed_load", classes=1, students=3, days=2)
    call_command("seed_load", clear=True)
    assert Student.objects.count() == sample_students
    assert not ClassGroup.objects.filter(name__startswith="LOAD-").exists()
