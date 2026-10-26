from django.core.exceptions import PermissionDenied

from .models import AuditLog
from .services import record


class DeniedRequestMiddleware:
    """Record a DENIED entry whenever a view refuses a request with PermissionDenied."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            record(
                getattr(request, "user", None),
                "Opened a page outside their role",
                AuditLog.Outcome.DENIED,
                detail=request.path,
            )
        return None
