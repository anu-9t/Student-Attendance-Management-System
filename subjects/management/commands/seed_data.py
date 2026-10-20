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

CLASSES = [("CSE-5A", "CSE", 5), ("CSE-5B", "CSE", 5)]

SUBJECTS = [
    ("UE24CS341A", "Software Engineering", 5),
    ("UE24CS342A", "Computer Networks", 5),
    ("UE24CS343A", "Database Management Systems", 5),
]

# employee id, username, name
FACULTY = [("F001", "faculty1", "Sample Faculty One"), ("F002", "faculty2", "Sample Faculty Two")]

# Which faculty member teaches which subject to which class
ASSIGNMENTS = [
    ("F001", "UE24CS341A", "CSE-5A"),
    ("F001", "UE24CS341A", "CSE-5B"),
    ("F002", "UE24CS342A", "CSE-5A"),
    ("F002", "UE24CS343A", "CSE-5B"),
]

STUDENTS_PER_CLASS = 4


def ensure_user(username, role, **extra):
    user, _ = User.objects.get_or_create(username=username, defaults={"role": role, **extra})
    if not user.password or not user.has_usable_password():
        user.set_password(PASSWORD)
        user.save()
    return user


class Command(BaseCommand):
    help = "Create sample users, classes, subjects, time slots, assignments and the default threshold."

    def handle(self, *args, **options):
        ensure_user("admin", User.Role.ADMIN, is_staff=True, is_superuser=True)

        classes = {}
        for name, dept, sem in CLASSES:
            classes[name], _ = ClassGroup.objects.get_or_create(name=name, defaults={"department": dept, "semester": sem})

        subjects = {}
        for code, name, sem in SUBJECTS:
            subjects[code], _ = Subject.objects.get_or_create(code=code, defaults={"name": name, "semester": sem})

        faculty = {}
        for emp_id, username, name in FACULTY:
            user = ensure_user(username, User.Role.FACULTY)
            faculty[emp_id], _ = Faculty.objects.get_or_create(
                employee_id=emp_id, defaults={"user": user, "name": name, "department": "CSE"}
            )

        for emp_id, code, class_name in ASSIGNMENTS:
            SubjectAssignment.objects.get_or_create(
                faculty=faculty[emp_id], subject=subjects[code], class_group=classes[class_name]
            )

        number = 1
        for class_name in classes:
            for _ in range(STUDENTS_PER_CLASS):
                user = ensure_user(f"student{number}", User.Role.STUDENT)
                Student.objects.get_or_create(
                    srn=f"PES2UG24CS{90 + number:03d}",
                    defaults={
                        "user": user,
                        "class_group": classes[class_name],
                        "name": f"Sample Student {number}",
                        "email": f"student{number}@example.com",
                    },
                )
                number += 1

        for label, start, end in SLOTS:
            TimeSlot.objects.get_or_create(label=label, defaults={"start_time": dt.time(start), "end_time": dt.time(end)})

        SystemSetting.objects.get_or_create(key="attendance_threshold", defaults={"value": "75"})
        self.stdout.write(self.style.SUCCESS("Sample data loaded."))
