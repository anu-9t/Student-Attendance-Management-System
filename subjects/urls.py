from django.urls import path

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.subject_list, name="list"),
    path("add/", views.subject_add, name="add"),
    path("<int:pk>/edit/", views.subject_edit, name="edit"),
]
