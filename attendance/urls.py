from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("select/", views.select_class, name="select"),
    path("mark/<int:class_id>/<int:subject_id>/", views.mark, name="mark"),
]
