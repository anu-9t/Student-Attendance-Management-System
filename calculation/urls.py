from django.urls import path

from . import views

app_name = "calculation"

urlpatterns = [
    path("", views.my_percentage, name="mine"),
]
