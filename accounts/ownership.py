"""Who may see which records (SAM-SEC-004).

- A student sees only their own records.
- A faculty member sees the students and subjects of the classes assigned to them.
- The administrator sees everything.

Views that show a student's attendance call get_visible_student(); lists use
visible_students(). Both work from the logged-in user, never from anything the
browser sends, so changing an id in the URL can't reach someone else's records.
"""
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment

from .models import User


def student_profile(user):
    """The Student record behind a student login, or None."""
    if not user.is_authenticated or user.role != User.Role.STUDENT:
        return None
    return Student.objects.filter(user=user).select_related("class_group").first()


def faculty_profile(user):
    """The active Faculty record behind a faculty login, or None."""
    if not user.is_authenticated or user.role != User.Role.FACULTY:
        return None
    return Faculty.objects.filter(user=user, is_active=True).first()


def faculty_assignments(user):
    """The class/subject pairs the faculty user teaches (empty for everyone else)."""
    faculty = faculty_profile(user)
    if faculty is None:
        return SubjectAssignment.objects.none()
    return SubjectAssignment.objects.filter(faculty=faculty).select_related("class_group", "subject")


def visible_students(user):
    """Every student this user is allowed to see."""
    if not user.is_authenticated:
        return Student.objects.none()
    if user.role == User.Role.ADMIN:
        return Student.objects.all()
    if user.role == User.Role.FACULTY:
        classes = faculty_assignments(user).values("class_group")
        return Student.objects.filter(class_group__in=classes)
    if user.role == User.Role.STUDENT:
        return Student.objects.filter(user=user)
    return Student.objects.none()


def can_see_student(user, student):
    return visible_students(user).filter(pk=student.pk).exists()


def get_visible_student(user, pk):
    """The student with this id, if the user may see them. 404 if there's no such
    student, 403 (recorded in the audit log) if it's someone else's record."""
    student = get_object_or_404(Student, pk=pk)
    if not can_see_student(user, student):
        raise PermissionDenied("That student's records belong to someone else.")
    return student


def teaches(user, class_group, subject):
    """True if the faculty user is assigned this subject for this class."""
    return faculty_assignments(user).filter(class_group=class_group, subject=subject).exists()
