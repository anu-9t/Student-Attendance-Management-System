from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect

from .forms import LoginForm
from .roles import home_url_for


class SamsLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SamsLogoutView(LogoutView):
    # Logging out needs a POST (the logout button is a small form),
    # which stops another site from logging people out with a link.
    pass


@login_required
def home(request):
    """Send each user to the dashboard for their role."""
    return redirect(home_url_for(request.user))
