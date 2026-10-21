from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.SamsLoginView.as_view(), name="login"),
    path("logout/", views.SamsLogoutView.as_view(), name="logout"),
]
