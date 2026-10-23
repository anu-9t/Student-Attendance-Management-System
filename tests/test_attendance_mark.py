import pytest
from django.core.management import call_command

from accounts.models import User
from students.models import Student
from subjects.models import SubjectAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def faculty_client(client):
    call_command("seed_data")
    client.force_login(User.objects.get(username="faculty1"))
    return client


def own_assignment():
    return SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()


# SAM-F-011: the marking sheet


def test_marking_sheet_lists_the_active_students_of_the_class(faculty_client):
    a = own_assignment()
    Student.objects.filter(srn="PES2UG24CS092").update(is_active=False)  # in CSE-5A, deactivated
    response = faculty_client.get(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/")
    assert response.status_code == 200
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        assert s.srn.encode() in response.content
    assert b"PES2UG24CS092" not in response.content
    assert b"Period 1" in response.content


def test_selected_pair_links_to_the_marking_sheet(faculty_client):
    a = own_assignment()
    response = faculty_client.get("/attendance/select/", {"class_id": a.class_group_id, "subject_id": a.subject_id})
    assert f"/attendance/mark/{a.class_group_id}/{a.subject_id}/".encode() in response.content


def test_marking_sheet_for_someone_elses_class_is_refused(faculty_client):
    other = SubjectAssignment.objects.exclude(faculty__user__username="faculty1").first()
    assert faculty_client.get(f"/attendance/mark/{other.class_group_id}/{other.subject_id}/").status_code == 404


# SAM-F-012 and SAM-F-013: saving, and refusing duplicates


def sheet(a, slots, statuses=None, date="2026-10-23"):
    data = {"date": date, "slots": [s.pk for s in slots]}
    for s in Student.objects.filter(class_group=a.class_group, is_active=True):
        data[f"status_{s.pk}"] = (statuses or {}).get(s.srn, "PRESENT")
    return data


def test_saving_stores_one_row_per_student_per_slot(faculty_client):
    from attendance.models import Attendance
    from subjects.models import TimeSlot

    a = own_assignment()
    slot = TimeSlot.objects.get(label="Period 1")
    response = faculty_client.post(
        f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", sheet(a, [slot], {"PES2UG24CS092": "ABSENT"})
    )
    assert response.status_code == 302
    assert Attendance.objects.count() == 4
    assert Attendance.objects.get(student__srn="PES2UG24CS092").status == "ABSENT"
    assert Attendance.objects.filter(status="PRESENT").count() == 3


def test_a_two_hour_lab_is_saved_as_two_classes(faculty_client):
    from attendance.models import Attendance
    from subjects.models import TimeSlot

    a = own_assignment()
    slots = list(TimeSlot.objects.filter(label__in=["Period 4", "Period 5"]))
    faculty_client.post(f"/attendance/mark/{a.class_group_id}/{a.subject_id}/", sheet(a, slots))
    assert Attendance.objects.filter(student__srn="PES2UG24CS091").count() == 2


def test_marking_the_same_slot_twice_is_refused_and_saves_nothing(faculty_client):
    from attendance.models import Attendance
    from subjects.models import TimeSlot

    a = own_assignment()
    p1 = TimeSlot.objects.get(label="Period 1")
    p2 = TimeSlot.objects.get(label="Period 2")
    url = f"/attendance/mark/{a.class_group_id}/{a.subject_id}/"
    faculty_client.post(url, sheet(a, [p1]))
    response = faculty_client.post(url, sheet(a, [p1, p2]))
    assert response.status_code == 200
    assert b"already saved" in response.content
    assert Attendance.objects.count() == 4  # Period 2 was not saved either


def test_future_dates_and_missing_slots_are_refused(faculty_client):
    from attendance.models import Attendance
    from subjects.models import TimeSlot

    a = own_assignment()
    url = f"/attendance/mark/{a.class_group_id}/{a.subject_id}/"
    r1 = faculty_client.post(url, sheet(a, [TimeSlot.objects.first()], date="2099-01-01"))
    r2 = faculty_client.post(url, sheet(a, []))
    assert b"future date" in r1.content
    assert b"at least one time slot" in r2.content
    assert Attendance.objects.count() == 0
