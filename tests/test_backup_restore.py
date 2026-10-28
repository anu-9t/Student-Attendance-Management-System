"""SAM-NF-005: database backup and restore."""
import gzip
import json

import pytest
from django.core.management import call_command

from audit.models import AuditLog

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded():
    call_command("seed_data")


def test_backup_writes_a_compressed_file(seeded, tmp_path):
    call_command("backup_db", dir=str(tmp_path))
    files = list(tmp_path.glob("sams-*.json.gz"))
    assert len(files) == 1
    data = json.loads(gzip.open(files[0], "rt", encoding="utf-8").read())
    models = {row["model"] for row in data}
    assert {"students.student", "accounts.user", "subjects.subject"} <= models
    assert "sessions.session" not in models


def test_backup_is_recorded_in_the_audit_log(seeded, tmp_path):
    call_command("backup_db", dir=str(tmp_path))
    entry = AuditLog.objects.get(action="Backed up the database")
    assert entry.detail.startswith("sams-")


def test_keep_removes_the_oldest_backups(seeded, tmp_path):
    for name in ["sams-20261001-000000.json.gz", "sams-20261002-000000.json.gz", "sams-20261003-000000.json.gz"]:
        (tmp_path / name).write_bytes(b"")
    call_command("backup_db", dir=str(tmp_path), keep=2)
    names = sorted(f.name for f in tmp_path.glob("sams-*.json.gz"))
    assert len(names) == 2
    assert "sams-20261001-000000.json.gz" not in names


# Restore


@pytest.mark.django_db(transaction=True)
def test_restore_brings_back_deleted_records(tmp_path):
    from attendance.models import Attendance
    from students.models import Student

    call_command("seed_data")
    call_command("backup_db", dir=str(tmp_path))
    backup = next(tmp_path.glob("sams-*.json.gz"))
    students = Student.objects.count()

    Attendance.objects.all().delete()
    Student.objects.filter(srn="PES2UG24CS091").update(name="Changed by mistake")
    Student.objects.filter(srn="PES2UG24CS098").delete()

    call_command("restore_db", str(backup), yes=True)
    assert Student.objects.count() == students
    assert Student.objects.get(srn="PES2UG24CS091").name != "Changed by mistake"


@pytest.mark.django_db(transaction=True)
def test_restored_logins_still_work(client, tmp_path):
    call_command("seed_data")
    call_command("backup_db", dir=str(tmp_path))
    call_command("restore_db", str(next(tmp_path.glob("sams-*.json.gz"))), yes=True)
    response = client.post("/login/", {"username": "faculty1", "password": "Sams@12345"})
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_restore_is_recorded_in_the_audit_log(tmp_path):
    call_command("seed_data")
    call_command("backup_db", dir=str(tmp_path))
    call_command("restore_db", str(next(tmp_path.glob("sams-*.json.gz"))), yes=True)
    assert AuditLog.objects.filter(action="Restored the database").count() == 1
    assert AuditLog.objects.filter(action="Backed up the database").count() == 1  # kept from the backup


def test_restore_asks_first(seeded, tmp_path, monkeypatch):
    from django.core.management.base import CommandError

    call_command("backup_db", dir=str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt: "no")
    with pytest.raises(CommandError, match="Cancelled"):
        call_command("restore_db", str(next(tmp_path.glob("sams-*.json.gz"))))


def test_restore_refuses_a_missing_file(seeded, tmp_path):
    from django.core.management.base import CommandError

    with pytest.raises(CommandError, match="No such backup file"):
        call_command("restore_db", str(tmp_path / "nope.json.gz"), yes=True)


def test_a_failed_backup_is_recorded_and_leaves_no_file(seeded, tmp_path, monkeypatch):
    import attendance.management.commands.backup_db as backup

    def broken(*args, **kwargs):
        if args and args[0] == "dumpdata":
            raise OSError("disk full")
        return original(*args, **kwargs)

    original = backup.call_command
    monkeypatch.setattr(backup, "call_command", broken)
    with pytest.raises(OSError):
        call_command("backup_db", dir=str(tmp_path))
    assert not list(tmp_path.glob("sams-*.json.gz"))
    assert AuditLog.objects.get(action="Backup failed").outcome == AuditLog.Outcome.FAILED
