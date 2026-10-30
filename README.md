# Student Attendance Management System (SAMS)

![Status](https://img.shields.io/badge/status-Sprint%202%20complete-brightgreen)
![Course](https://img.shields.io/badge/course-UE24CS341A-blue)
![Team](https://img.shields.io/badge/team-Team%203-lightgrey)

A web-based attendance system built as the Software Engineering mini-project for **UE24CS341A** at
PES University. Faculty mark attendance for their classes, students see their own percentage and
history, and the administrator manages students, faculty, subjects and reports.

## Contents
- [What it does](#what-it-does)
- [Run it](#run-it)
- [Documents](#documents)
- [Architecture](#architecture)
- [Testing](#testing)
- [How we work](#how-we-work)
- [Repository layout](#repository-layout)
- [Project status](#project-status)
- [Team](#team)

## What it does

| Role | Can do |
|---|---|
| **Administrator** | Add, edit, search and deactivate students and faculty; manage subjects, one-hour time slots and who teaches what; set the low-attendance threshold; read the audit log; all reports |
| **Faculty** | Pick an assigned class and subject; mark attendance for one or more time slots; correct a saved session with a reason; see students below the threshold; reports for their own subjects |
| **Student** | See their percentage per subject, low-attendance warnings, and their history, newest first |

Reports are student-wise, subject-wise and class-wise, with a date range, CSV and PDF download, and a print view.
Every page needs a login; each role only reaches its own pages; students only ever see their own records;
an account locks for 15 minutes after 5 failed logins; every admin change, refused page and failed login is
in the audit log.

## Run it

With Docker (Nginx with HTTPS, Django with gunicorn, MySQL 8.0):

```
cp .env.example .env              # then change the passwords
docker compose up --build
docker compose exec web python manage.py seed_data
```

Open https://localhost/ (the local certificate is self-signed) and log in as `admin`, `faculty1` or
`student1`, password `Sams@12345`. Quick local runs with SQLite, backups and more are in
[DEVELOPING.md](DEVELOPING.md).

## Documents

| Document | Version | Files |
|---|---|---|
| Software Requirements Specification (SRS) | 1.1 | [PDF](docs/SRS_v1.1.pdf) · [Word](docs/SRS_v1.1.docx) |
| Software Architecture and Design (SAD) | 1.1 | [PDF](docs/SAD_v1.1.pdf) · [Word](docs/SAD_v1.1.docx) |
| Software Test Plan (STP) | 1.1 | [PDF](docs/STP_v1.1.pdf) · [Word](docs/STP_v1.1.docx) |
| Deviations from the documents | — | [docs/DEVIATIONS.md](docs/DEVIATIONS.md) |
| Requirements traceability (status) | — | [docs/testing/rtm.md](docs/testing/rtm.md) |
| Test summary report (Sprint 2) | — | [docs/testing/test-summary.md](docs/testing/test-summary.md) |
| Test data | — | [docs/testing/test-data.md](docs/testing/test-data.md) |
| Sprint videos | — | [docs/videos/](docs/videos/) |

Version 1.1 of each document is "updated to reflect the work done in Sprints 1 and 2". The submitted
version 1.0 files are kept unchanged in [docs/v1.0/](docs/v1.0/).

## Architecture

A layered Django monolith (SAD 3.5), one app per module:

```text
Browser ──HTTPS──> Nginx ──> Django (gunicorn) ──> MySQL 8.0
                              │
                              ├─ accounts      login, roles, access control, ownership checks
                              ├─ dashboards    one dashboard per role
                              ├─ students      student records (deactivate, never delete)
                              ├─ faculty       faculty records
                              ├─ subjects      subjects, one-hour time slots, who teaches what
                              ├─ attendance    select, mark, modify; backup_db / restore_db
                              ├─ calculation   percentage and history
                              ├─ notification  threshold and low-attendance flags
                              ├─ reports       reports, CSV / PDF / print
                              └─ audit         append-only audit log
```

Tech stack: Python 3.12, Django 5.2, MySQL 8.0, Bootstrap 5, django-axes (lockout), reportlab (PDF),
Docker and docker-compose, Nginx. CI: GitHub Actions with ruff, pytest and coverage.py, Bandit, SonarCloud.

## Testing

```
DB_ENGINE=sqlite pytest            # the whole suite, about 30 seconds
```

358 automated tests, 96% line and branch coverage. All 32 requirements and all 7 use cases have test
cases, and the 7 non-functional test cases (performance, load, usability, maintainability, reliability,
recovery, data protection) are automated too. CI runs everything on MySQL for every pull request; a pull
request can only be merged with CI green and a reviewer's approval. Details:
[test summary](docs/testing/test-summary.md).

## How we work

- The backlog is on the GitHub Project board (**SAMS Backlog**): one issue per requirement or task, with story
  points, an owner and a sprint milestone.
- One branch per issue (`feature/<issue>-<words>`), a pull request with a reviewer from SAD Table 3, CI green,
  then the repository owner merges. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository layout

```text
.github/            CI workflow, pull request template
accounts/ ... audit/  one Django app per module (see Architecture)
sams/               settings and root URLs
templates/          page templates, one folder per module
tests/              pytest test cases (unit, use-case, non-functional)
nginx/              Nginx image with a self-signed certificate for local HTTPS
docs/               SRS, SAD, STP (v1.1 and v1.0), deviations, testing reports, videos
Dockerfile, docker-compose.yml, requirements*.txt, ruff.toml, sonar-project.properties
```

## Project status

| Sprint | Dates | Outcome |
|---|---|---|
| Sprint 1 | 19 to 23 Oct 2026 | Set-up (skeleton, Docker, CI), login and access control, lockout, dashboards, student, faculty and subject management, select class, mark attendance; first test cases. Tag `sprint-1` |
| Sprint 2 | 26 to 30 Oct 2026 | Audit log, ownership checks, percentage, history, threshold and flags, modify attendance, reports with export, backup and restore, availability and data protection, performance; all remaining and non-functional test cases; documents v1.1. Tags `sprint-2`, `v1.0` |

## Team

Team 3, PES University

| Name | SRN | Role (STP Section 9) |
|---|---|---|
| Anmol Vyas | PES2UG24CS072 | Developer |
| Anupam Rajesh Tiwari | PES2UG24CS073 | Developer, repository owner |
| Anupriya | PES2UG24CS074 | QA Lead |
| Anusha G | PES2UG24CS075 | Test Engineer |

Academic coursework project (UE24CS341A, PES University).
