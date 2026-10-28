"""Back up the whole database to one compressed file (SAM-NF-005).

    python manage.py backup_db              # writes backups/sams-YYYYMMDD-HHMMSS.json.gz
    python manage.py backup_db --keep 14    # ...and keeps only the newest 14 backups

The file is plain JSON (Django's dumpdata), so it restores into MySQL or SQLite alike.
"""
import gzip
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from audit.services import record

# Tables Django rebuilds by itself, or that only hold short-lived data.
EXCLUDE = ["contenttypes", "auth.permission", "sessions", "admin.logentry", "axes"]


def backup_dir():
    return Path(getattr(settings, "BACKUP_DIR", settings.BASE_DIR / "backups"))


class Command(BaseCommand):
    help = "Back up the database to backups/sams-<date>.json.gz"

    def add_arguments(self, parser):
        parser.add_argument("--dir", help="Folder to write to (default: backups/)")
        parser.add_argument("--keep", type=int, default=0, help="Keep only the newest N backups (0 = keep all)")

    def handle(self, *args, **options):
        folder = Path(options["dir"]) if options["dir"] else backup_dir()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"sams-{timezone.localtime():%Y%m%d-%H%M%S}.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as out:
            call_command(
                "dumpdata", natural_foreign=True, natural_primary=True, exclude=EXCLUDE, indent=None, stdout=out
            )
        record(None, "Backed up the database", detail=path.name)

        if options["keep"] > 0:
            old = sorted(folder.glob("sams-*.json.gz"))[: -options["keep"]]
            for f in old:
                f.unlink()

        size_kb = path.stat().st_size / 1024
        self.stdout.write(self.style.SUCCESS(f"Backup written: {path} ({size_kb:.0f} KB)"))
