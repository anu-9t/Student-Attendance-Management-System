from .models import User

# Where each role lands after logging in (SAM-F-003).
# The dashboard pages themselves are built in the dashboards module.
HOME_FOR_ROLE = {
    User.Role.ADMIN: "/dashboard/admin/",
    User.Role.FACULTY: "/dashboard/faculty/",
    User.Role.STUDENT: "/dashboard/student/",
}


def home_url_for(user):
    return HOME_FOR_ROLE.get(user.role, "/login/")
