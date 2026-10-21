from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render


class SamsLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class SamsLogoutView(LogoutView):
    # Logging out needs a POST (the logout button is a small form),
    # which stops another site from logging people out with a link.
    pass


@login_required
def home(request):
    return render(request, "accounts/home.html")
