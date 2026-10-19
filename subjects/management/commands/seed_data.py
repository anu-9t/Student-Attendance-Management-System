"""Loads sample data for development and testing: python manage.py seed_data (safe to run twice)."""
import datetime as dt
import os

from django.core.management.base import BaseCommand

from accounts.models import User
from faculty.models import Faculty
from notification.models import SystemSetting
from students.models import ClassGroup, Student
from subjects.models import Subject, SubjectAssignment, TimeSlot

# Development-only default. Set SEED_PASSWORD to use another one.
PASSWORD = os.environ.get("SEED_PASSWORD", "Sams@12345")

SLOTS = [("Period 1", 9, 10), ("Period 2", 10, 11), ("Period 3", 11, 12),
         ("Period 4", 13, 14), ("Period 5", 14, 15), ("Period 6", 15, 16)]


class Command(BaseCommand):
    help = "Create sample users, class, subjects, time slots and the default threshold."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username="admin", defaults={"role": User.Role.ADMIN, "is_staff": True, "is_superuser": True})
        fac_user, _ = User.objects.get_or_create(username="faculty1", defaults={"role": User.Role.FACULTY})
        stu_users = [User.objects.get_or_create(username=f"student{i}", defaults={"role": User.Role.STUDENT})[0] for i in (1, 2, 3)]
        for u in [admin, fac_user, *stu_users]:
            if not u.has_usable_password():
                u.set_password(PASSWORD)
                u.save()

        cls, _ = ClassGroup.objects.get_or_create(name="CSE-3A", defaults={"department": "CSE", "semester": 5})
        fac, _ = Faculty.objects.get_or_create(employee_id="F001", defaults={"user": fac_user, "name": "Sample Faculty", "department": "CSE"})
        subj, _ = Subject.objects.get_or_create(code="UE24CS341A", defaults={"name": "Software Engineering", "semester": 5})
        SubjectAssignment.objects.get_or_create(faculty=fac, subject=subj, class_group=cls)

        for i, u in enumerate(stu_users, start=1):
            Student.objects.get_or_create(srn=f"PES2UG24CS09{i}", defaults={"user": u, "class_group": cls, "name": f"Sample Student {i}", "email": f"student{i}@example.com"})

        for label, start, end in SLOTS:
            TimeSlot.objects.get_or_create(label=label, defaults={"start_time": dt.time(start), "end_time": dt.time(end)})

        SystemSetting.objects.get_or_create(key="attendance_threshold", defaults={"value": "75"})
        self.stdout.write(self.style.SUCCESS("Sample data loaded."))
