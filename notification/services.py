"""The low-attendance threshold (SAM-F-017). Stored in SystemSetting; 75% if never set."""
from decimal import Decimal, InvalidOperation

from audit.services import record

from .models import SystemSetting

KEY = "attendance_threshold"
DEFAULT = 75.0


def get_threshold():
    value = SystemSetting.objects.filter(key=KEY).values_list("value", flat=True).first()
    try:
        return float(Decimal(value)) if value is not None else DEFAULT
    except InvalidOperation:
        return DEFAULT


def set_threshold(value, user):
    old = get_threshold()
    SystemSetting.objects.update_or_create(key=KEY, defaults={"value": f"{value:g}"})
    record(user, "Changed the attendance threshold", detail=f"{old:g}% -> {value:g}%")


def is_below(percent, threshold=None):
    """True when there were classes and the percentage is under the threshold."""
    if percent is None:
        return False
    return percent < (get_threshold() if threshold is None else threshold)
