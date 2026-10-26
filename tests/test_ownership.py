"""SAM-SEC-004: students see only their own records; faculty only their classes."""
import pytest
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import Http404

from accounts.models import User
from accounts.ownership import (
    can_see_student,
    faculty_assignments,
    get_visible_student,
    student_profile,
    teaches,
    visible_students,
)
from students.models import ClassGroup, Student
from subjects.models import Subject

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


def user(name):
    return User.objects.get(username=name)


def test_admin_sees_every_student(seeded):
    assert visible_students(user("admin")).count() == Student.objects.count()


def test_student_sees_only_themselves(seeded):
    me = user("student1")
    assert list(visible_students(me)) == [Student.objects.get(user=me)]


def test_student_cannot_open_another_students_record(seeded):
    other = Student.objects.exclude(user__username="student1").first()
    with pytest.raises(PermissionDenied):
        get_visible_student(user("student1"), other.pk)


def test_student_can_open_their_own_record(seeded):
    mine = Student.objects.get(user__username="student1")
    assert get_visible_student(user("student1"), mine.pk) == mine


def test_unknown_student_is_404_not_403(seeded):
    with pytest.raises(Http404):
        get_visible_student(user("admin"), 999999)


def test_faculty_sees_only_students_in_their_classes(seeded):
    other_class = ClassGroup.objects.create(name="CSE-5C", department="CSE", semester=5)
    outsider = Student.objects.create(class_group=other_class, srn="PES2UG24CS300", name="Not Taught")
    faculty = user("faculty1")
    seen = set(visible_students(faculty))
    assert outsider not in seen
    assert Student.objects.filter(class_group__name="CSE-5A").first() in seen
    assert not can_see_student(faculty, outsider)


def test_teaches_follows_the_assignments(seeded):
    se = Subject.objects.get(code="UE24CS341A")
    cse5a = ClassGroup.objects.get(name="CSE-5A")
    assert teaches(user("faculty1"), cse5a, se)
    assert not teaches(user("faculty2"), cse5a, se)
    assert not teaches(user("admin"), cse5a, se)


def test_other_roles_have_no_profile_or_assignments(seeded):
    assert student_profile(user("admin")) is None
    assert not faculty_assignments(user("student1")).exists()


# The checks in use on the pages built so far


def test_student_dashboard_shows_only_their_own_details(client, seeded):
    me = Student.objects.get(user__username="student1")
    other = Student.objects.exclude(pk=me.pk).first()
    client.force_login(me.user)
    body = client.get("/dashboard/student/").content.decode()
    assert me.srn in body
    assert other.srn not in body


def test_faculty_dashboard_lists_only_their_own_subjects(client, seeded):
    client.force_login(user("faculty2"))
    body = client.get("/dashboard/faculty/").content.decode()
    assert "UE24CS342A" in body
    assert "UE24CS341A" not in body


def test_faculty_cannot_open_a_class_they_dont_teach(client, seeded):
    se = Subject.objects.get(code="UE24CS341A")
    cse5a = ClassGroup.objects.get(name="CSE-5A")
    client.force_login(user("faculty2"))
    assert client.get(f"/attendance/mark/{cse5a.pk}/{se.pk}/").status_code == 404
    assert client.get(f"/attendance/select/?class_id={cse5a.pk}&subject_id={se.pk}").status_code == 404
