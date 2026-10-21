from django.urls import path

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.subject_list, name="list"),
    path("add/", views.subject_add, name="add"),
    path("<int:pk>/edit/", views.subject_edit, name="edit"),
    path("time-slots/", views.timeslot_list, name="timeslots"),
    path("time-slots/add/", views.timeslot_add, name="timeslot_add"),
    path("time-slots/<int:pk>/edit/", views.timeslot_edit, name="timeslot_edit"),
]
