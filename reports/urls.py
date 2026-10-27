from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("student/<int:pk>/", views.student_report, name="student"),
    path("subject/<int:class_id>/<int:subject_id>/", views.subject_report, name="subject"),
    path("class/<int:class_id>/", views.class_report, name="class"),
]
