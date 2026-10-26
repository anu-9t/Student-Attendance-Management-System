"""One place that writes audit entries (SAM-SEC-005).

Other modules call record() or log_admin_action(); they don't touch AuditLog directly.
"""
from .models import AuditLog


def record(user, action, outcome=AuditLog.Outcome.SUCCESS, target=None, detail=""):
    """Add one entry. target can be any saved model object, or None."""
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    return AuditLog.objects.create(
        user=user,
        action=action[:100],
        target_type=type(target).__name__ if target is not None else "",
        target_id=str(target.pk) if target is not None else "",
        outcome=outcome,
        detail=detail,
    )


def log_admin_action(request, action, target, detail=""):
    """Record a successful change made by the administrator (UC-05)."""
    return record(request.user, action, AuditLog.Outcome.SUCCESS, target=target, detail=detail)
