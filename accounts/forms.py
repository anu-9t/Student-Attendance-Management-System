from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    # Plain messages for the login page (SAM-F-002). The same message is
    # shown for a wrong username and a wrong password, so the page does
    # not tell anyone which usernames exist.
    error_messages = {
        "invalid_login": "Wrong username or password. Please try again.",
        "inactive": "This account has been deactivated. Please contact the administrator.",
    }
