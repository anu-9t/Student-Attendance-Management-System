from django.urls import path

from . import views

app_name = "dashboards"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("faculty/", views.faculty_dashboard, name="faculty"),
    path("student/", views.student_dashboard, name="student"),
]
