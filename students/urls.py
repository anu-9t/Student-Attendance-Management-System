from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.student_list, name="list"),
    path("add/", views.student_add, name="add"),
    path("<int:pk>/edit/", views.student_edit, name="edit"),
]
