from django.urls import path

from . import views

app_name = "faculty"

urlpatterns = [
    path("", views.faculty_list, name="list"),
    path("add/", views.faculty_add, name="add"),
    path("<int:pk>/edit/", views.faculty_edit, name="edit"),
    path("<int:pk>/deactivate/", views.faculty_deactivate, name="deactivate"),
]
