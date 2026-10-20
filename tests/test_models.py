import datetime as dt

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from students.models import ClassGroup, Student
from subjects.models import TimeSlot

pytestmark = pytest.mark.django_db


def test_time_slot_must_end_after_it_starts():
    slot = TimeSlot(label="Broken", start_time=dt.time(10), end_time=dt.time(9))
    with pytest.raises(ValidationError):
        slot.full_clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        slot.save()


def test_a_normal_time_slot_is_fine():
    slot = TimeSlot(label="Period 1", start_time=dt.time(9), end_time=dt.time(10))
    slot.full_clean()
    slot.save()
    assert TimeSlot.objects.count() == 1


def test_students_are_listed_by_srn():
    group = ClassGroup.objects.create(name="CSE-5A", department="CSE", semester=5)
    for srn in ["PES2UG24CS093", "PES2UG24CS091", "PES2UG24CS092"]:
        Student.objects.create(class_group=group, srn=srn, name=srn)
    assert [s.srn for s in Student.objects.all()] == ["PES2UG24CS091", "PES2UG24CS092", "PES2UG24CS093"]
