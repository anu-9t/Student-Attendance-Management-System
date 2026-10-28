"""Low-attendance alerts for the dashboards (SAM-F-017).

    {% load alerts %}
    {% low_attendance_for user as low %}      on the student dashboard
    {% flagged_for user as flagged %}         on the faculty dashboard
"""
from django import template

from accounts.ownership import faculty_assignments, student_profile
from notification.services import flagged_students, get_threshold, low_subjects

register = template.Library()


@register.simple_tag
def threshold():
    return get_threshold()


@register.simple_tag
def low_attendance_for(user):
    student = student_profile(user)
    return low_subjects(student) if student else []


@register.simple_tag
def flagged_for(user):
    return flagged_students(faculty_assignments(user))
