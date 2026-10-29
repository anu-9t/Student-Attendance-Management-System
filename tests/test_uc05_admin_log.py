"""Test cases for UC-05 (Log Administrative Action), TC-SEC-05 (SAM-SEC-005).

Test owner: Anupriya (STP Section 9). UC-05 is included by UC-04: every change the
administrator makes, and every refused or failed attempt, ends up in the audit log.
"""
import pytest
from django.core.management import call_command

from audit.models import AuditLog
from faculty.models import Faculty
from students.models import ClassGroup, Student

pytestmark = pytest.mark.django_db

PASSWORD = "Sams@12345"


def login(client, username, password=PASSWORD):
    client.post("/logout/")
    return client.post("/login/", {"username": username, "password": password})


@pytest.fixture
def admin(client):
    call_command("seed_data")
    login(client, "admin")
    return client


def entries(action):
    return AuditLog.objects.filter(action=action)


def test_tc_uc05_01_adding_a_student_is_logged_with_who_and_what(admin):
    group = ClassGroup.objects.get(name="CSE-5B")
    admin.post("/students/add/", {"srn": "PES2UG24CS201", "name": "Logged Student", "email": "",
                                  "class_group": group.pk, "password": "Welcome@123"})
    entry = entries("Added a student").get()
    assert entry.user.username == "admin"
    assert entry.outcome == "SUCCESS"
    assert entry.target_type == "Student"
    assert entry.target_id == str(Student.objects.get(srn="PES2UG24CS201").pk)


def test_tc_uc05_02_an_edit_records_which_fields_changed(admin):
    student = Student.objects.get(srn="PES2UG24CS091")
    admin.post(f"/students/{student.pk}/edit/", {"srn": student.srn, "name": "New Name", "email": student.email,
                                                 "class_group": student.class_group_id})
    assert entries("Updated a student").get().detail == "name"


def test_tc_uc05_03_deactivations_are_logged(admin):
    student = Student.objects.get(srn="PES2UG24CS091")
    member = Faculty.objects.get(employee_id="F002")
    admin.post(f"/students/{student.pk}/deactivate/")
    admin.post(f"/faculty/{member.pk}/deactivate/")
    assert entries("Deactivated a student").count() == 1
    assert entries("Deactivated a faculty member").count() == 1


def test_tc_uc05_04_assignment_changes_are_logged(admin):
    from subjects.models import SubjectAssignment

    a = SubjectAssignment.objects.first()
    admin.post(f"/subjects/assignments/{a.pk}/remove/")
    assert entries("Removed a subject assignment").count() == 1


def test_tc_uc05_05_a_refused_page_is_logged_as_denied(client):
    call_command("seed_data")
    login(client, "faculty1")
    client.get("/students/")
    entry = AuditLog.objects.get(outcome="DENIED")
    assert entry.user.username == "faculty1"
    assert entry.detail == "/students/"


def test_tc_uc05_06_a_failed_login_is_logged(client):
    call_command("seed_data")
    login(client, "admin", password="not-the-password")
    entry = AuditLog.objects.get(outcome="FAILED")
    assert "username=admin" in entry.detail


def test_tc_uc05_07_nobody_can_change_or_delete_the_log(admin):
    login(admin, "admin", password="wrong")  # leaves one FAILED entry
    login(admin, "admin")
    entry = AuditLog.objects.get(outcome="FAILED")
    with pytest.raises(PermissionError):
        entry.delete()
    entry.detail = "edited"
    with pytest.raises(PermissionError):
        entry.save()
    assert AuditLog.objects.get(pk=entry.pk).detail != "edited"
    # and the admin site offers no add, change or delete
    assert admin.get(f"/admin/audit/auditlog/{entry.pk}/delete/").status_code in (403, 302)


def test_tc_uc05_08_admin_reads_and_filters_the_log(admin):
    login(admin, "faculty1")
    admin.get("/students/")  # one DENIED entry
    login(admin, "admin")
    body = admin.get("/audit/", {"outcome": "DENIED"}).content.decode()
    assert "faculty1" in body
    assert "/students/" in body


@pytest.mark.parametrize("username", ["faculty1", "student1"])
def test_tc_uc05_09_only_the_admin_reads_the_log(client, username):
    call_command("seed_data")
    login(client, username)
    assert client.get("/audit/").status_code == 403
