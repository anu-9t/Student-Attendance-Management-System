# Code coverage report (line coverage)

Owner: Anusha G (Test Engineer). Measured with coverage.py during the [unit test run](../unit-tests/unit-test-report.md)
of 30 Oct 2026, 17:45 IST on `main` at `a5c5066` (v1.0). Settings in `.coveragerc`: branch coverage on; migrations,
`manage.py`, `sams/wsgi.py` and the tests themselves are left out.

| Measure | Result | Target (STP Section 14, CI gate) |
|---|---|---|
| Line (statement) coverage | **96.9%** (1342 of 1385 statements) | at least 85% |
| Branch coverage | **88.1%** (229 of 260 branches); see the [branch coverage report](branch-coverage-report.md) | reported |
| Combined (what CI checks with `--fail-under=85`; coverage.py rounds it to 96%) | **95.5%** | at least 85% |
| Files fully covered | 50 of 69 | |

## By module

| App | Statements | Missed | Line coverage |
|---|---|---|---|
| `accounts` | 106 | 3 | 97.2% |
| `attendance` | 205 | 9 | 95.6% |
| `audit` | 90 | 3 | 96.7% |
| `calculation` | 85 | 1 | 98.8% |
| `dashboards` | 40 | 2 | 95.0% |
| `faculty` | 104 | 3 | 97.1% |
| `notification` | 88 | 1 | 98.9% |
| `reports` | 203 | 1 | 99.5% |
| `sams` | 63 | 6 | 90.5% |
| `students` | 198 | 3 | 98.5% |
| `subjects` | 203 | 11 | 94.6% |
| **Total** | **1385** | **43** | **96.9%** |

## Files with lines not run by any test

| File | Statements | Missed | Coverage | Missed lines |
|---|---|---|---|---|
| `accounts/ownership.py` | 39 | 2 | 94.9% | 46, 54 |
| `accounts/permissions.py` | 21 | 1 | 95.2% | 40 |
| `attendance/management/commands/backup_db.py` | 34 | 1 | 97.1% | 24 |
| `attendance/models.py` | 19 | 1 | 94.7% | 36 |
| `attendance/views.py` | 118 | 7 | 94.1% | 26, 35, 56, 64, 94, 95, 107 |
| `audit/admin.py` | 11 | 2 | 81.8% | 11, 14 |
| `audit/services.py` | 7 | 1 | 85.7% | 11 |
| `calculation/history.py` | 30 | 1 | 96.7% | 42 |
| `dashboards/views.py` | 32 | 2 | 93.8% | 30, 38 |
| `faculty/forms.py` | 28 | 1 | 96.4% | 34 |
| `faculty/views.py` | 52 | 2 | 96.2% | 37, 50 |
| `notification/models.py` | 6 | 1 | 83.3% | 11 |
| `reports/services.py` | 79 | 1 | 98.7% | 46 |
| `sams/settings.py` | 49 | 6 | 87.8% | 76, 133, 134, 135, 136, 138 |
| `students/forms.py` | 30 | 1 | 96.7% | 38 |
| `students/models.py` | 22 | 1 | 95.5% | 31 |
| `students/views.py` | 56 | 1 | 98.2% | 58 |
| `subjects/models.py` | 30 | 1 | 96.7% | 40 |
| `subjects/views.py` | 80 | 10 | 87.5% | 46, 70, 71, 72, 73, 74, 75, 76, 77, 78 |

Every requirement still has a passing test case ([RTM](../../testing/rtm.md)); the lines above are other paths
through the same code that no test happens to take. They are listed so they can be covered in maintenance.

## Files

- [html/index.html](html/index.html): the coverage.py report, file by file with every line marked (download the
  folder and open `index.html`, or browse it locally).
- [coverage.xml](coverage.xml): Cobertura XML, the format SonarCloud and CI read.
