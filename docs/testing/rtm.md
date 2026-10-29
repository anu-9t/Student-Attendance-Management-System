# Requirements Traceability Matrix: status (SRS Section 8, STP Section 13)

Kept up to date by the Test Engineer (Anusha G). Every one of the 32 requirements has at least
one automated test case; all of them run on every pull request in CI (GitHub Actions, MySQL 8.0).
Status as of 29 Oct 2026, end of Sprint 2 testing: **32 of 32 passing**.

## Functional (20)

| Requirement | What | Test case | Where (tests/) | Status |
|---|---|---|---|---|
| SAM-F-001 | Log in with username and password | TC-Auth-01 | test_login.py | Pass |
| SAM-F-002 | Reject a wrong login with a message | TC-Auth-02 | test_login.py, test_nfr_ux.py | Pass |
| SAM-F-003 | Role-based access and landing page | TC-Auth-03 | test_login.py, test_uc04_user_access.py | Pass |
| SAM-F-004 | Add a student | TC-Student-01 | test_students.py, test_uc04_user_access.py | Pass |
| SAM-F-005 | Update a student (deactivate, never delete) | TC-Student-02 | test_students.py | Pass |
| SAM-F-006 | Search students by SRN or name | TC-Student-03 | test_students.py | Pass |
| SAM-F-007 | Manage faculty | TC-Faculty-01 | test_faculty.py, test_uc04_user_access.py | Pass |
| SAM-F-008 | Manage subjects and time slots | TC-Subject-01 | test_subjects.py, test_tc_subjects.py | Pass |
| SAM-F-009 | Assign subjects to faculty, per class | TC-Subject-02 | test_subjects.py, test_tc_subjects.py | Pass |
| SAM-F-010 | Select an assigned class and subject | TC-Att-01 | test_attendance_select.py, test_uc01_uc02.py | Pass |
| SAM-F-011 | Mark each student present or absent | TC-Att-02 | test_attendance_mark.py, test_uc01_uc02.py | Pass |
| SAM-F-012 | Store attendance per student, subject, date and time slot | TC-Att-03 | test_attendance_mark.py, test_uc01_uc02.py | Pass |
| SAM-F-013 | Refuse duplicate attendance | TC-Att-04 | test_attendance_mark.py, test_uc01_uc02.py | Pass |
| SAM-F-014 | Modify attendance with a reason | TC-Att-05 | test_attendance_modify.py, test_tc_att05_modify.py | Pass |
| SAM-F-015 | Attendance percentage per subject | TC-Calc-01 | test_percentage.py, test_uc03_uc07.py | Pass |
| SAM-F-016 | Attendance history, newest first | TC-View-01 | test_history.py, test_uc03_uc07.py | Pass |
| SAM-F-017 | Threshold and low-attendance alerts | TC-Alert-01 | test_threshold.py, test_uc03_uc07.py | Pass |
| SAM-F-018 | Student-wise report | TC-Report-01 | test_reports.py, test_uc06_reports.py | Pass |
| SAM-F-019 | Subject-wise and class-wise reports | TC-Report-02 | test_reports.py, test_uc06_reports.py | Pass |
| SAM-F-020 | Download (CSV, PDF) and print reports | TC-Report-03 | test_report_export.py, test_uc06_reports.py | Pass |

## Non-functional (7)

| Requirement | What | Test case | Where (tests/) | Status |
|---|---|---|---|---|
| SAM-NF-001 | Pages answer within 3 seconds | TC-Perf-01 | test_nfr_perf.py, test_report_performance.py | Pass |
| SAM-NF-002 | Availability (restart, health checks) | TC-Reliability-01 | test_nfr_reliability.py, test_availability.py | Pass |
| SAM-NF-003 | Simple, usable interface | TC-UX-01 | test_nfr_ux.py, test_dashboards.py | Pass |
| SAM-NF-004 | Data protection | TC-Sec-01 | test_data_protection.py, test_lockout.py | Pass |
| SAM-NF-005 | Backup and recovery | TC-Recovery-01 | test_nfr_recovery.py, test_backup_restore.py | Pass |
| SAM-NF-006 | Maintainability | TC-Maint-01 | test_nfr_maint.py, test_architecture.py | Pass |
| SAM-NF-007 | Scalability, many users at once | TC-Load-01 | test_nfr_load.py, test_seed_load.py | Pass |

## Security (5)

| Requirement | What | Test case | Where (tests/) | Status |
|---|---|---|---|---|
| SAM-SEC-001 | Every page needs a login | TC-SEC-01 | test_access_control.py | Pass |
| SAM-SEC-002 | Role separation | TC-SEC-02 | test_access_control.py, test_uc04_user_access.py | Pass |
| SAM-SEC-003 | Hashed passwords, login lockout | TC-SEC-03 | test_login.py, test_lockout.py | Pass |
| SAM-SEC-004 | Students see only their own records | TC-SEC-04 | test_ownership.py, test_uc03_uc07.py | Pass |
| SAM-SEC-005 | Audit log of admin actions | TC-SEC-05 | test_audit.py, test_uc05_admin_log.py | Pass |
