"""Restore the database from a file made by backup_db (SAM-NF-005).

    python manage.py restore_db backups/sams-20261028-110000.json.gz

Everything currently in the database is replaced, so it asks first (or pass --yes).
"""
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from audit.services import record


class Command(BaseCommand):
    help = "Replace the database with the contents of a backup file"

    def add_arguments(self, parser):
        parser.add_argument("file", help="A backups/sams-*.json.gz file")
        parser.add_argument("--yes", action="store_true", help="Don't ask for confirmation")

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(f"No such backup file: {path}")
        if not options["yes"]:
            answer = input(f"This replaces everything in the database with {path.name}. Type 'restore' to go on: ")
            if answer.strip() != "restore":
                raise CommandError("Cancelled, nothing was changed.")

        with transaction.atomic():
            call_command("flush", interactive=False, verbosity=0)
            call_command("loaddata", str(path), verbosity=0)
            record(None, "Restored the database", detail=path.name)
        self.stdout.write(self.style.SUCCESS(f"Restored from {path}"))
