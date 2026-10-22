from functools import wraps

from django.shortcuts import render

from .signals import access_denied


def _deny(request, sender):
    access_denied.send(sender=sender, request=request, user=request.user, path=request.path)
    return render(request, "403.html", status=403)


def role_required(*roles):
    """Allow a view only for the given roles (SAM-SEC-002).

    Usage:
        @role_required(User.Role.ADMIN)
        def manage_students(request): ...
    """

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in roles:
                return view(request, *args, **kwargs)
            return _deny(request, view)

        return wrapped

    return decorator


class RoleRequiredMixin:
    """The same check for class-based views: set allowed_roles on the view."""

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        return _deny(request, self.__class__)
