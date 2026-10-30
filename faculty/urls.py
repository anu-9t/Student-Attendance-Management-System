from django.urls import path

from . import views


app_name = "faculty"

urlpatterns = [
    path("assignments/", views.assignments, name="assignments"),
]
