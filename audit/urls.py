from django.urls import path

from . import views

app_name = "audit"

urlpatterns = [
    path("", views.log_list, name="list"),
]
