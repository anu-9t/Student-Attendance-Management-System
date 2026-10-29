"""TC-Recovery-01 (SAM-NF-005): after losing data, a backup brings everything back.

Owner: Anusha G. With a term's worth of data loaded, take a backup, lose data in three
different ways, restore, and check that every count, percentage and login is as before.
Recovery has to finish within 60 seconds for this amount of data.
"""
import time

import pytest
from django.core.management import call_command

from accounts.models import User
from attendance.models import Attendance
from audit.models import AuditLog
from calculation.services import student_summary
from students.models import ClassGroup, Student
from subjects.models import Subject, SubjectAssignment

pytestmark = pytest.mark.django_db(transaction=True)

LIMIT_SECONDS = 60


def snapshot():
    probe = Student.objects.order_by("srn").first()
    return {
        "students": Student.objects.count(),
        "classes": ClassGroup.objects.count(),
        "subjects": Subject.objects.count(),
        "assignments": SubjectAssignment.objects.count(),
        "attendance": Attendance.objects.count(),
        "present": Attendance.objects.filter(status="PRESENT").count(),
        "users": User.objects.count(),
        "probe": [(r.subject.code, r.attended, r.total) for r in student_summary(probe)],
    }


@pytest.fixture
def backed_up(tmp_path):
    call_command("seed_data", verbosity=0)
    call_command("seed_load", classes=2, students=30, days=10, verbosity=0)
    before = snapshot()
    call_command("backup_db", dir=str(tmp_path))
    return before, next(tmp_path.glob("sams-*.json.gz"))


def restore(path):
    start = time.perf_counter()
    call_command("restore_db", str(path), yes=True)
    seconds = time.perf_counter() - start
    print(f"TC-Recovery-01 restore of {path.stat().st_size / 1024:.0f} KB took {seconds:.2f}s")
    return seconds


def test_tc_recovery_01a_deleted_attendance_comes_back(backed_up):
    before, path = backed_up
    Attendance.objects.filter(student__class_group__name="LOAD-1").delete()
    assert snapshot() != before
    assert restore(path) < LIMIT_SECONDS
    assert snapshot() == before


def test_tc_recovery_01b_wrong_edits_are_undone(backed_up):
    before, path = backed_up
    Attendance.objects.update(status="ABSENT")
    Student.objects.update(name="Overwritten")
    restore(path)
    assert snapshot() == before
    assert not Student.objects.filter(name="Overwritten").exists()


def test_tc_recovery_01c_an_emptied_database_is_rebuilt(backed_up):
    before, path = backed_up
    call_command("flush", interactive=False, verbosity=0)
    assert Student.objects.count() == 0
    restore(path)
    assert snapshot() == before


def test_tc_recovery_01d_logins_and_pages_work_after_recovery(client, backed_up):
    _, path = backed_up
    call_command("flush", interactive=False, verbosity=0)
    restore(path)
    for username in ["admin", "faculty1", "student1"]:
        client.post("/logout/")
        assert client.post("/login/", {"username": username, "password": "Sams@12345"}).status_code == 302
        assert client.get("/", follow=True).status_code == 200


def test_tc_recovery_01e_the_restore_is_on_record(backed_up):
    _, path = backed_up
    restore(path)
    assert AuditLog.objects.filter(action="Restored the database", detail=path.name).count() == 1
