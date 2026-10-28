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
