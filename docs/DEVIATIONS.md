# Deviations from the submitted documents

Deliverables Part-2 asks for deviations from the submitted SRS, SAD and Test Plan to be documented and
explained. This file lists every one we know of, and why. The documents themselves are now at version 1.1
("updated to reflect the work done in Sprints 1 and 2"); the submitted version 1.0 files are in
[docs/v1.0/](v1.0/).

In short: **no requirement was dropped or added**, the architecture, modules, data model and the
architecture decisions (SAD 4.7) were followed, and the division of work in SAD Table 1 was kept. The
differences are details that were open in the documents or that changed once the code existed.

## 1. Requirements (SRS v1.0 → v1.1)

| Where | v1.0 said | What we built | Why |
|---|---|---|---|
| SAM-F-012, SAM-F-013, UC-01 | Attendance per student, subject and date; duplicates per student, subject and date | Per student, subject, date **and one-hour time slot**; duplicates refused per slot; a two-hour lab is two records | The college takes attendance by the hour. Decided in the SAD (ADR-004, from STP 13.1); SRS reworded in v1.1 |
| SAM-F-014 | Authorised faculty modify a record | The assigned faculty member corrects a whole date and slot at once, and must give a reason (kept in the audit log) | A reason makes the audit entry useful; one correction usually covers several students |
| SAM-F-017 | Warning below "the required percentage" | Threshold set by the admin, 75% by default; warnings on the student dashboard and attendance page; a list for faculty | The SRS left the value and where warnings appear open |
| SAM-F-018 to 020 | Student-, subject- and class-wise reports, downloadable and printable | As specified, plus a date range; downloads as CSV and PDF | UC-06 mentions a date range; CSV and PDF are the two formats in SAD 3.6 |
| RTM (Section 8) | Every status N | Every status P | All 32 requirements have passing test cases |

## 2. Design (SAD v1.0 → v1.1, new Section 6)

| Area | v1.0 design | As built | Why |
|---|---|---|---|
| URLs (4.3) | `/manage/students/`, `/faculty/assignments/`, `/student/attendance/`, `/attendance/<id>/edit/`, `/manage/settings/threshold/`, `/manage/audit/` | `/students/`, `/attendance/select/`, `/percentage/` and `/history/`, `/attendance/modify/<class>/<subject>/`, `/notifications/threshold/`, `/audit/` | Each module includes its own URLs (SAD 3.5), so the paths follow the module names. Access rules unchanged |
| Error codes (4.3) | 400 for invalid input, 409 for duplicate attendance | Form re-shown with a message (200); nothing saved | That is how Django forms report errors; the user sees the same message |
| Modify attendance (4.3.2) | Faculty or admin | Assigned faculty only | The admin has no attendance pages, which keeps "who changed it" clear |
| Faculty low-attendance warning (4.3.3) | Through the reports | A list on the faculty dashboard, plus red percentages in reports | Visible without opening a report |
| Backups (3.6, 4.3.3) | mysqldump wrapped in a command | `backup_db` / `restore_db` with Django's JSON dump, compressed | Works the same on MySQL and SQLite, so the recovery test (TC-Recovery-01) runs in CI. Nightly runs: host cron (DEVELOPING.md) |
| Continuous delivery (3.6) | Deploy to staging | Image built and published to GitHub Container Registry on every merge; the demo machine runs it with docker compose | No always-on staging machine for a class project |
| Quality gates | Tests with coverage, Bandit, SonarCloud | Also ruff (lint and complexity), a migration check, an 85% coverage floor | Cheap checks that catch mistakes before review. SonarCloud needs the `SONAR_TOKEN` secret |
| Data model (4.1.1) | Indexes on (student, subject, date) and (subject, date) | Two more: (subject, student, status) and (class, active) | Report counts and class lists (TC-Perf-01, #30) |
| Security (3.9) | HTTPS, hashing, lockout, role checks, audit | Also: idle sessions expire after 30 minutes; HTTPS-only cookies and safe headers in production; HSTS switchable | Data protection, SAM-NF-004 (#29). HSTS stays off with the self-signed certificate |
| Health check (4.4) | /health/ for Docker | /health/ also queries the database, 503 when it can't | A container with a lost database is restarted instead of serving errors (TC-Reliability-01) |

## 3. Test plan (STP v1.0 → v1.1)

| Where | v1.0 said | v1.1 / what we did | Why |
|---|---|---|---|
| Sections 3 and 13 | No SAM-F-008, 009, 014 | Added, with owners (Anmol: subjects and assignments; Anupam: modification) | Planned in SAD 4.6 |
| Section 4 | Load and stress testing out of scope; performance a single spot check | TC-Perf-01 times every main page; TC-Load-01 runs 20 users at once; both automated | Cheap to automate once the seed_load data existed |
| Section 6 | Manual test cases, GitHub Actions planned | Every test case automated (pytest), GitHub Actions on every pull request, Docker, SonarCloud, Bandit, coverage.py, ruff | The pipeline was set up in Sprint 1 |
| Section 7 | Provisional dates | Actual dates of Sprints 1 and 2 | Phase-2 dates were not known when the STP was written |
| Section 13 | Manual scripts to be written | Appendix A: every test case with its files, owner and status | Automated test cases replace the manual scripts |

## 4. Process

| Topic | Note |
|---|---|
| Sprints | Sprint 1: 19 to 23 Oct (tag `sprint-1`); Sprint 2: 26 to 30 Oct (tags `sprint-2`, `v1.0`). Milestones and the project board track both |
| Branches and reviews | 1 branch and 1 pull request per issue (one shared branch for the non-functional tests, one commit per owner); every pull request reviewed by the partner in SAD Table 3 and merged by the repository owner |
| Work split | As in SAD Table 1; who built and tested what is in SAD v1.1, Section 6.3 |
