# Unit test report

Owner: Anusha G (Test Engineer). STP Section 8 (test deliverables) and Section 14 (metrics).

| | |
|---|---|
| Code tested | `main` at `a5c5066`, the frozen Sprint 2 code (tags `sprint-2`, `v1.0`) |
| Run | 30 Oct 2026, 17:45 IST, `DB_ENGINE=sqlite coverage run -m pytest` (CI runs the same suite on MySQL 8.0) |
| Environment | Python 3.12, Django 5.2, pytest 8, pytest-django, SQLite |
| Result | **358 passed, 0 failed, 0 skipped, 358 in total** |
| Time | 36.4 s |

Every test is automated and runs on every pull request (GitHub Actions). The tests are written at three levels:
unit tests per module (models, forms, views, commands), integration tests per use case (`test_uc*.py`, a whole
flow through several modules), and the non-functional test cases (`test_nfr_*.py`). The system-level run against
a live server is the [system validation report](../system-validation/system-validation-report.md).

## Results by test file

| Test file (tests/) | Test cases (RTM) | Tests | Passed | Failed | Skipped | Time (s) |
|---|---|---|---|---|---|---|
| `test_access_control.py` | TC-SEC-01, TC-SEC-02 | 10 | 10 | 0 | 0 | 0.56 |
| `test_architecture.py` | TC-Maint-01 | 33 | 33 | 0 | 0 | 0.13 |
| `test_attendance_mark.py` | TC-Att-02, TC-Att-03, TC-Att-04 | 7 | 7 | 0 | 0 | 0.56 |
| `test_attendance_modify.py` | TC-Att-05 | 11 | 11 | 0 | 0 | 0.73 |
| `test_attendance_select.py` | TC-Att-01 | 4 | 4 | 0 | 0 | 0.25 |
| `test_audit.py` | TC-SEC-05 | 14 | 14 | 0 | 0 | 0.98 |
| `test_availability.py` | TC-Reliability-01 | 8 | 8 | 0 | 0 | 0.02 |
| `test_backup_restore.py` | TC-Recovery-01 | 9 | 9 | 0 | 0 | 1.04 |
| `test_dashboards.py` | TC-UX-01 | 10 | 10 | 0 | 0 | 0.24 |
| `test_data_protection.py` | TC-Sec-01 | 5 | 5 | 0 | 0 | 0.14 |
| `test_faculty.py` | TC-Faculty-01 | 5 | 5 | 0 | 0 | 0.33 |
| `test_history.py` | TC-View-01 | 11 | 11 | 0 | 0 | 0.69 |
| `test_lockout.py` | TC-SEC-03, TC-Sec-01 | 5 | 5 | 0 | 0 | 0.38 |
| `test_login.py` | TC-Auth-01, TC-Auth-02, TC-Auth-03, TC-SEC-03 | 9 | 9 | 0 | 0 | 0.10 |
| `test_models.py` | - | 3 | 3 | 0 | 0 | 0.01 |
| `test_nfr_load.py` | TC-Load-01 | 1 | 1 | 0 | 0 | 3.23 |
| `test_nfr_maint.py` | TC-Maint-01 | 12 | 12 | 0 | 0 | 0.10 |
| `test_nfr_perf.py` | TC-Perf-01 | 5 | 5 | 0 | 0 | 5.03 |
| `test_nfr_recovery.py` | TC-Recovery-01 | 5 | 5 | 0 | 0 | 9.46 |
| `test_nfr_reliability.py` | TC-Reliability-01 | 5 | 5 | 0 | 0 | 0.20 |
| `test_nfr_ux.py` | TC-Auth-02, TC-UX-01 | 13 | 13 | 0 | 0 | 1.21 |
| `test_ownership.py` | TC-SEC-04 | 11 | 11 | 0 | 0 | 0.48 |
| `test_percentage.py` | TC-Calc-01 | 12 | 12 | 0 | 0 | 0.58 |
| `test_report_export.py` | TC-Report-03 | 8 | 8 | 0 | 0 | 0.51 |
| `test_report_performance.py` | TC-Perf-01 | 5 | 5 | 0 | 0 | 0.35 |
| `test_reports.py` | TC-Report-01, TC-Report-02 | 18 | 18 | 0 | 0 | 0.93 |
| `test_seed_load.py` | TC-Load-01 | 5 | 5 | 0 | 0 | 0.20 |
| `test_smoke.py` | - | 6 | 6 | 0 | 0 | 0.18 |
| `test_students.py` | TC-Student-01, TC-Student-02, TC-Student-03 | 8 | 8 | 0 | 0 | 0.43 |
| `test_subjects.py` | TC-Subject-01, TC-Subject-02 | 10 | 10 | 0 | 0 | 0.52 |
| `test_tc_att05_modify.py` | TC-Att-05 (UC-01) | 7 | 7 | 0 | 0 | 0.56 |
| `test_tc_subjects.py` | TC-Subject-01, TC-Subject-02 (UC-06) | 9 | 9 | 0 | 0 | 0.49 |
| `test_testdata.py` | - | 2 | 2 | 0 | 0 | 0.19 |
| `test_threshold.py` | TC-Alert-01 | 16 | 16 | 0 | 0 | 0.69 |
| `test_uc01_uc02.py` | TC-Att-01, TC-Att-02, TC-Att-03, TC-Att-04 (UC-01, UC-02) | 10 | 10 | 0 | 0 | 0.64 |
| `test_uc03_uc07.py` | TC-Alert-01, TC-Calc-01, TC-SEC-04, TC-View-01 (UC-03, UC-07) | 18 | 18 | 0 | 0 | 1.19 |
| `test_uc04_user_access.py` | TC-Auth-03, TC-Faculty-01, TC-SEC-02, TC-Student-01 (UC-04) | 8 | 8 | 0 | 0 | 0.58 |
| `test_uc05_admin_log.py` | TC-SEC-05 (UC-05) | 10 | 10 | 0 | 0 | 0.58 |
| `test_uc06_reports.py` | TC-Report-01, TC-Report-02, TC-Report-03 (UC-06) | 10 | 10 | 0 | 0 | 1.25 |
| **Total** | | **358** | **358** | **0** | **0** | **35.74** |

## Slowest tests

| Test | Time (s) | Why |
|---|---|---|
| `test_nfr_load.py::test_tc_load_01_twenty_users_at_once` | 3.23 | non-functional: many requests or a large data set by design |
| `test_nfr_recovery.py::test_tc_recovery_01e_the_restore_is_on_record` | 2.13 | non-functional: many requests or a large data set by design |
| `test_nfr_recovery.py::test_tc_recovery_01a_deleted_attendance_comes_back` | 1.89 | non-functional: many requests or a large data set by design |
| `test_nfr_recovery.py::test_tc_recovery_01d_logins_and_pages_work_after_recovery` | 1.88 | non-functional: many requests or a large data set by design |
| `test_nfr_recovery.py::test_tc_recovery_01b_wrong_edits_are_undone` | 1.86 | non-functional: many requests or a large data set by design |

## Files

- [unit-test-report.html](unit-test-report.html): every test with its result and time (open in a browser).
- [unit-test-results.xml](unit-test-results.xml): the same results in JUnit XML, as CI produces them.
- Coverage of this run: [code coverage](../coverage/code-coverage-report.md), [branch coverage](../coverage/branch-coverage-report.md).

## How to reproduce

```
DB_ENGINE=sqlite coverage run -m pytest --junitxml=unit-test-results.xml
coverage report
```
