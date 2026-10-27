from django.urls import path

from . import history

app_name = "history"

urlpatterns = [
    path("", history.my_history, name="mine"),
    path("student/<int:pk>/", history.student_history, name="student"),
]
