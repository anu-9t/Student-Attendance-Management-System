from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.models import User
from accounts.permissions import role_required

from .forms import ThresholdForm
from .services import get_threshold, set_threshold


@role_required(User.Role.ADMIN)
def threshold(request):
    """SAM-F-017: the administrator sets the low-attendance threshold."""
    form = ThresholdForm(request.POST or None, initial={"threshold": get_threshold()})
    if request.method == "POST" and form.is_valid():
        set_threshold(float(form.cleaned_data["threshold"]), request.user)
        messages.success(request, f"Threshold set to {form.cleaned_data['threshold']:g}%.")
        return redirect("notification:threshold")
    return render(request, "notification/threshold.html", {"form": form, "current": get_threshold()})
