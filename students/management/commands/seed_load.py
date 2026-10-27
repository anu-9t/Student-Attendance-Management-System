"""Fill the database with a realistic amount of data for scalability checks (SAM-NF-007).

    python manage.py seed_data                       # the small sample set, needed first
    python manage.py seed_load                       # 6 classes x 60 students, 60 teaching days
    python manage.py seed_load --classes 2 --students 10 --days 5

Classes are named LOAD-1, LOAD-2, ... and students PES2UG24LD0001, ... so the extra data is easy
to spot and to remove again with --clear. Running it twice doesn't create duplicates.
"""
import datetime as dt
import random
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from attendance.models import Attendance
from faculty.models import Faculty
from students.models import ClassGroup, Student
from subjects.models import Subject, SubjectAssignment, TimeSlot

PREFIX = "LOAD-"


class Command(BaseCommand):
    help = "Add load-test classes, students and attendance on top of seed_data"

    def add_arguments(self, parser):
        parser.add_argument("--classes", type=int, default=6)
        parser.add_argument("--students", type=int, default=60, help="students per class")
        parser.add_argument("--days", type=int, default=60, help="teaching days of attendance")
        parser.add_argument("--clear", action="store_true", help="remove the load-test data instead")

    def handle(self, *args, **opts):
        if opts["clear"]:
            self._clear()
            return
        subjects = list(Subject.objects.order_by("code"))
        slots = list(TimeSlot.objects.order_by("start_time"))
        faculty = list(Faculty.objects.filter(is_active=True).order_by("employee_id"))
        if not (subjects and slots and faculty):
            raise CommandError("Run `python manage.py seed_data` first.")

        started = time.monotonic()
        # Fixed seed: the same data on every machine. Not used for anything secret.
        rng = random.Random(42)  # nosec B311
        with transaction.atomic():
            groups = self._classes(opts["classes"], subjects, faculty)
            students = self._students(groups, opts["students"])
            rows = self._attendance(students, subjects, slots, faculty[0], opts["days"], rng)
        took = time.monotonic() - started
        self.stdout.write(
            self.style.SUCCESS(
                f"{len(groups)} classes, {len(students)} students, {rows} new attendance rows in {took:.1f}s"
            )
        )

    def _classes(self, count, subjects, faculty):
        groups = []
        for i in range(1, count + 1):
            group, _ = ClassGroup.objects.get_or_create(
                name=f"{PREFIX}{i}", defaults={"department": "CSE", "semester": 5}
            )
            for j, subject in enumerate(subjects):
                SubjectAssignment.objects.get_or_create(
                    faculty=faculty[j % len(faculty)], subject=subject, class_group=group
                )
            groups.append(group)
        return groups

    def _students(self, groups, per_class):
        wanted = []
        for gi, group in enumerate(groups):
            for k in range(per_class):
                n = gi * per_class + k + 1
                wanted.append(Student(class_group=group, srn=f"PES2UG24LD{n:04d}", name=f"Load Student {n}"))
        existing = set(Student.objects.filter(srn__in=[s.srn for s in wanted]).values_list("srn", flat=True))
        Student.objects.bulk_create([s for s in wanted if s.srn not in existing], batch_size=500)
        return list(Student.objects.filter(srn__in=[s.srn for s in wanted]).select_related("class_group"))

    def _attendance(self, students, subjects, slots, marked_by, days, rng):
        start = dt.date.today() - dt.timedelta(days=days * 7 // 5 + 1)
        teaching_days = [d for d in (start + dt.timedelta(i) for i in range(days * 2)) if d.weekday() < 5][:days]
        done = set(
            Attendance.objects.filter(student__in=students).values_list("student_id", "subject_id", "date", "time_slot_id")
        )
        batch, created = [], 0
        for day_index, day in enumerate(teaching_days):
            for si, subject in enumerate(subjects):
                slot = slots[(day_index + si) % len(slots)]
                for st in students:
                    if (st.pk, subject.pk, day, slot.pk) in done:
                        continue
                    status = Attendance.Status.PRESENT if rng.random() < 0.8 else Attendance.Status.ABSENT
                    batch.append(
                        Attendance(student=st, subject=subject, date=day, time_slot=slot, status=status, marked_by=marked_by)
                    )
                    if len(batch) >= 2000:
                        Attendance.objects.bulk_create(batch)
                        created += len(batch)
                        batch = []
        Attendance.objects.bulk_create(batch)
        return created + len(batch)

    def _clear(self):
        with transaction.atomic():
            students = Student.objects.filter(class_group__name__startswith=PREFIX)
            rows, _ = Attendance.objects.filter(student__in=students).delete()
            students.delete()
            SubjectAssignment.objects.filter(class_group__name__startswith=PREFIX).delete()
            ClassGroup.objects.filter(name__startswith=PREFIX).delete()
        self.stdout.write(self.style.SUCCESS(f"Removed the load-test data ({rows} attendance rows)."))
