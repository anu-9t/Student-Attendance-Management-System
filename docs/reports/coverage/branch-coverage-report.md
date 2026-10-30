# Branch coverage report

Owner: Anusha G (Test Engineer). Same run as the [code coverage report](code-coverage-report.md): 30 Oct 2026, 17:45 IST,
`main` at `a5c5066` (v1.0), coverage.py with `branch = True`.

Branch coverage counts both ways out of every decision (`if`, `for`, `while`, `try`): a branch is covered when
some test takes it. A *partial* branch is a decision where the tests took only one of its ways.

| Measure | Result |
|---|---|
| Branches | 260 |
| Covered | **229 (88.1%)** |
| Not taken by any test | 31 |
| Decisions only partly covered | 29 |

## By module

| App | Branches | Covered | Partial decisions | Branch coverage |
|---|---|---|---|---|
| `accounts` | 20 | 17 | 3 | 85.0% |
| `attendance` | 54 | 48 | 6 | 88.9% |
| `audit` | 10 | 9 | 1 | 90.0% |
| `calculation` | 8 | 7 | 1 | 87.5% |
| `dashboards` | 10 | 8 | 2 | 80.0% |
| `faculty` | 18 | 11 | 7 | 61.1% |
| `notification` | 12 | 12 | 0 | 100.0% |
| `reports` | 44 | 43 | 1 | 97.7% |
| `sams` | 4 | 2 | 2 | 50.0% |
| `students` | 42 | 38 | 4 | 90.5% |
| `subjects` | 38 | 34 | 2 | 89.5% |
| **Total** | **260** | **229** | **29** | **88.1%** |

## Branches no test takes

| File | Line | Untaken way | Code at that line |
|---|---|---|---|
| `accounts/ownership.py` | 45 | line 46 | `if not user.is_authenticated:` |
| `accounts/ownership.py` | 52 | line 54 | `if user.role == User.Role.STUDENT:` |
| `accounts/permissions.py` | 39 | line 40 | `if request.user.is_authenticated and request.user.role in self.allowed` |
| `attendance/management/commands/restore_db.py` | 29 | line 32 | `if answer.strip() != "restore":` |
| `attendance/views.py` | 25 | line 26 | `if faculty_profile(request.user) is None:` |
| `attendance/views.py` | 34 | line 35 | `if class_id is None or subject_id is None:` |
| `attendance/views.py` | 55 | line 56 | `if faculty is None:` |
| `attendance/views.py` | 63 | line 64 | `if request.user.role != User.Role.FACULTY:` |
| `attendance/views.py` | 106 | line 107 | `if value not in Attendance.Status.values:` |
| `audit/services.py` | 10 | line 11 | `if user is not None and not getattr(user, "is_authenticated", False):` |
| `calculation/history.py` | 41 | line 42 | `if student is None:` |
| `dashboards/views.py` | 28 | line 30 | `if user.role == "STUDENT":` |
| `dashboards/views.py` | 37 | line 38 | `if template is None:` |
| `faculty/forms.py` | 33 | line 34 | `if User.objects.filter(username__iexact=username).exists():` |
| `faculty/forms.py` | 44 | line 46 | `if commit:` |
| `faculty/views.py` | 22 | line 24 | `if not show_inactive:` |
| `faculty/views.py` | 32 | line 37 | `if request.method == "POST" and form.is_valid():` |
| `faculty/views.py` | 45 | line 50 | `if request.method == "POST" and form.is_valid():` |
| `faculty/views.py` | 57 | line 65 | `if request.method == "POST":` |
| `faculty/views.py` | 60 | line 63 | `if member.user:` |
| `reports/services.py` | 45 | line 46 | `if date_to:` |
| `sams/settings.py` | 73 | line 76 | `if os.environ.get("DB_ENGINE", "mysql") == "sqlite":` |
| `sams/settings.py` | 132 | line 133 | `if not DEBUG:` |
| `students/forms.py` | 37 | line 38 | `if User.objects.filter(username__iexact=srn).exists():` |
| `students/forms.py` | 50 | line 52 | `if commit:` |
| `students/views.py` | 53 | line 58 | `if request.method == "POST" and form.is_valid():` |
| `students/views.py` | 69 | line 72 | `if student.user:` |
| `subjects/views.py` | 41 | line 46 | `if request.method == "POST" and form.is_valid():` |
| `subjects/views.py` | 73 | line 74 | `if request.method == "POST" and form.is_valid():` |
| `subjects/views.py` | 73 | line 78 | `if request.method == "POST" and form.is_valid():` |
| `subjects/views.py` | 101 | line 105 | `if request.method == "POST":` |

Each requirement's behaviour is still tested end to end ([RTM](../../testing/rtm.md)); these branches are
other ways through the same code (for example a check that a logged-out user never reaches because an earlier
check already stopped them). They are the first candidates for extra unit tests in maintenance
([maintenance plan](../../maintenance-plan.md)).

The line-by-line view, with partial branches marked in yellow, is in [html/index.html](html/index.html).
