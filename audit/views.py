from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from accounts.models import User
from accounts.permissions import role_required

from .models import AuditLog


@role_required(User.Role.ADMIN)
def log_list(request):
    """SAM-SEC-005: the administrator reads the audit log, newest first."""
    entries = AuditLog.objects.select_related("user").order_by("-timestamp", "-pk")
    outcome = request.GET.get("outcome", "")
    if outcome in AuditLog.Outcome.values:
        entries = entries.filter(outcome=outcome)
    query = request.GET.get("q", "").strip()
    if query:
        entries = entries.filter(
            Q(action__icontains=query) | Q(detail__icontains=query) | Q(user__username__icontains=query)
        )
    page = Paginator(entries, 50).get_page(request.GET.get("page"))
    return render(
        request,
        "audit/log_list.html",
        {"page": page, "outcome": outcome, "query": query, "outcomes": AuditLog.Outcome.choices},
    )
