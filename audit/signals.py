"""Listen for refusals and failed logins and write them to the audit log.

Refused pages come from two places: the role checks in accounts.permissions send
the access_denied signal, and older views raise PermissionDenied, which the
middleware in audit/middleware.py catches.
"""
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

from accounts.signals import access_denied

from .models import AuditLog
from .services import record


@receiver(access_denied)
def page_refused(sender, request, user, path, **kwargs):
    record(user, "Opened a page outside their role", AuditLog.Outcome.DENIED, detail=path)


@receiver(user_login_failed)
def login_failed(sender, credentials, request=None, **kwargs):
    username = credentials.get("username", "")
    ip = request.META.get("REMOTE_ADDR", "") if request is not None else ""
    record(None, "Failed login", AuditLog.Outcome.FAILED, detail=f"username={username} ip={ip}")
