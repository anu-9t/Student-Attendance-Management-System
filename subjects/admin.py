from django.contrib import admin

from .models import Subject, SubjectAssignment, TimeSlot

admin.site.register(Subject)
admin.site.register(TimeSlot)
admin.site.register(SubjectAssignment)
