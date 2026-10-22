from django.dispatch import Signal

# Sent whenever someone is refused a page because of their role.
# The audit module listens for it and records a DENIED entry, so this
# module does not need to know how auditing works.
# Arguments: request, user, path
access_denied = Signal()
