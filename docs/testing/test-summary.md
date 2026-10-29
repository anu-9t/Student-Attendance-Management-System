# Test summary report, Sprint 2 (STP Section 8, metrics)

Prepared by Anusha G (Test Engineer), 29 Oct 2026, for the code on the Sprint 2 branches
(everything merged into `main` on 29 Oct). Full traceability: [rtm.md](rtm.md).
Test data: [test-data.md](test-data.md).

## Results

| Measure | Result | Target |
|---|---|---|
| Automated tests | 358, all passing | all pass |
| Requirements with a passing test case | 32 of 32 (20 functional, 7 non-functional, 5 security) | 32 |
| Use cases with test cases | 7 of 7 (UC-01 to UC-07) | 7 |
| Line and branch coverage | 96% | at least 85% (CI gate) |
| Lint (ruff), complexity at most 10 | clean | clean |
| Bandit security scan (medium and high) | 0 issues | 0 |
| Open defects | 0 | 0 |

## Use-case test cases and owners (STP Section 13)

| Use case | Test cases | Owner | File (tests/) | Tests |
|---|---|---|---|---|
| UC-01 Mark Attendance, UC-02 Select Class and Subject | TC-Att-01 to TC-Att-05 | Anupam | test_uc01_uc02.py, test_tc_att05_modify.py | 17 |
| UC-03 View Attendance Percentage | TC-Calc-01, TC-Alert-01 | Anusha | test_uc03_uc07.py | 11 |
| UC-04 Manage User Access | TC-Student-01 to 03, TC-Faculty-01, TC-SEC-02 | Anupriya | test_uc04_user_access.py | 8 |
| UC-05 Log Administrative Action | TC-SEC-05 | Anupriya | test_uc05_admin_log.py | 10 |
| UC-06 Generate Reports | TC-Report-01 to 03 (and TC-Subject-01, 02) | Anmol | test_uc06_reports.py, test_tc_subjects.py | 19 |
| UC-07 View Attendance History | TC-View-01, TC-SEC-04 | Anusha | test_uc03_uc07.py | 7 |

## Non-functional test cases

Measured on a developer laptop with SQLite, the same tests CI runs against MySQL.

| Test case | Owner | What was measured | Result |
|---|---|---|---|
| TC-Perf-01 (SAM-NF-001) | Anmol | 16 main pages for each role, plus CSV and PDF downloads and saving a 60-student sheet, with about 7,500 extra attendance rows | slowest page 36 ms, PDF 164 ms, save 26 ms; limit 3 s |
| TC-Load-01 (SAM-NF-007) | Anupriya | 20 users at once, 200 page views | 0 errors, median 52 ms, 95th percentile 663 ms; limit 3 s |
| TC-Reliability-01 (SAM-NF-002) | Anupriya | lost database, crashing request, failed save | health check returns 503; next request works; plain error pages; nothing half-saved |
| TC-Recovery-01 (SAM-NF-005) | Anusha | backup, then lost, wrongly edited and emptied data | everything restored identically in about 1.5 s; logins work; restore is in the audit log |
| TC-UX-01 (SAM-NF-003) | Anupam | titles, labels, one-click tasks, way home and out, plain errors on 16 pages | all pass; one unlabelled filter found and fixed |
| TC-Maint-01 (SAM-NF-006) | Anmol | lint, complexity, CI gates, tests per module | all pass |

## Defects found during Sprint 2 testing

| Found by | Where | Defect | Fixed in |
|---|---|---|---|
| TC-UX-01 | Audit log page | The outcome filter had no label for screen readers | #36 (same commit) |
| TC-Reliability-01 | /health/ | The health check said "ok" even when the database was unreachable | #36 |
| Lint check (ruff) | dashboards, manage.py, wsgi.py | Unsorted imports, two imports on one line | #31 |

## Not covered, and why (STP Section 4)

- Cross-browser checks beyond Chrome: manual spot checks only.
- Load beyond 20 simultaneous users and a real network: out of scope for a class project; TC-Load-01
  runs inside one Python process, so its timings are pessimistic compared with the gunicorn server.
