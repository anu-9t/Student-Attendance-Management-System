# User stories

Owner: Anupam Rajesh Tiwari (Product Owner). Every item on the GitHub backlog (the **SAMS Backlog** project board)
written as a user story, with its acceptance criteria, owner, story points and sprint. The same story and criteria
are at the top of each backlog issue on GitHub. How the team estimated and ran the sprints is in
[agile-process.md](agile-process.md).

The stories come from the SRS: each functional and non-functional requirement became one backlog item (two closely
related requirements share one, for example SAM-F-002/003), plus the set-up, testing and documentation items from
SAD Table 1. The user in each story is the SRS actor (administrator, faculty member, student); set-up and testing
items are written for the developer, QA lead or evaluator who needs them. A story is done when every acceptance
criterion is met, its test cases pass in CI, the review partner has approved the pull request and the Product
Owner has merged it.

## Backlog at a glance

| Story | Title | Owner | Points | Sprint | Requirement | Use case |
|---|---|---|---|---|---|---|
| [SETUP-01](#setup-01) | Django skeleton, data model, migrations and seed script | Anmol | 2 | 1 | Foundation (SAD Figure 4.1) | - |
| [SETUP-02](#setup-02) | Dockerfile, docker-compose and Nginx environment | Anmol | 2 | 1 | SAM-NF-002, SAM-NF-004 | - |
| [SETUP-03](#setup-03) | GitHub Actions pipeline: tests and coverage, Bandit, SonarCloud, image build | Anupriya | 2 | 1 | SAM-NF-006 | - |
| [SAM-F-001](#sam-f-001) | Login with username and password | Anupam | 1 | 1 | SAM-F-001 | UC-04 |
| [SAM-F-002/003](#sam-f-002003) | Reject invalid login; role-based redirect (Admin, Faculty, Student) | Anupam | 1 | 1 | SAM-F-002, SAM-F-003 | UC-04 |
| [SAM-F-004](#sam-f-004) | Add student | Anusha | 1 | 1 | SAM-F-004 | UC-04 |
| [SAM-F-005/006](#sam-f-005006) | Update and search student; deactivate instead of delete | Anusha | 1 | 1 | SAM-F-005, SAM-F-006 | UC-04 |
| [SAM-F-007](#sam-f-007) | Manage faculty | Anusha | 1 | 1 | SAM-F-007 | UC-04 |
| [SAM-F-008](#sam-f-008) | Manage subjects and time slots | Anupriya | 1 | 1 | SAM-F-008 | UC-04 |
| [SAM-F-009](#sam-f-009) | Assign subjects to faculty | Anupriya | 1 | 1 | SAM-F-009 | UC-04 |
| [SAM-NF-003](#sam-nf-003) | Base templates and role dashboards | Anusha | 2 | 1 | SAM-NF-003 | - |
| [SAM-SEC-001/002](#sam-sec-001002) | Default-deny access control: login required, role boundaries | Anupam | 1 | 1 | SAM-SEC-001, SAM-SEC-002 | UC-04 |
| [SAM-SEC-003](#sam-sec-003) | Password hashing and login lockout (django-axes) | Anupam | 1 | 1 | SAM-SEC-003 | UC-04 |
| [SAM-F-010](#sam-f-010) | Select class and subject | Anmol | 1 | 1 | SAM-F-010 | UC-02 |
| [SAM-F-011](#sam-f-011) | Mark each student Present or Absent (marking sheet, one or more time slots) | Anmol | 1 | 1 | SAM-F-011 | UC-01 |
| [SAM-F-012/013](#sam-f-012013) | Store attendance in one transaction; reject duplicates per student, subject, date, time slot | Anmol | 1 | 1 | SAM-F-012, SAM-F-013 | UC-01 |
| [TEST-01](#test-01) | Test cases and execution: Mark Attendance, Select Class and Subject (UC-01, UC-02) and attendance modification (SAM-F-014) | Anupam | 3 | 1 | SAM-F-010 to 014 | UC-01, UC-02 |
| [TEST-03](#test-03) | Test cases and execution: Manage User Access, Log Administrative Action (UC-04, UC-05); quality gates and PR review rules | Anupriya | 4 | 1 | SAM-F-001 to 007, SAM-SEC-001 to 005 | UC-04, UC-05 |
| [SAM-F-014](#sam-f-014) | Modify attendance with a reason | Anmol | 1 | 2 | SAM-F-014 | UC-01 |
| [SAM-F-015](#sam-f-015) | Calculate attendance percentage per subject | Anupriya | 1 | 2 | SAM-F-015 | UC-03 |
| [SAM-F-016](#sam-f-016) | Student attendance history (newest first) | Anupriya | 1 | 2 | SAM-F-016 | UC-07 |
| [SAM-F-017](#sam-f-017) | Threshold setting and low-attendance flags | Anupriya | 2 | 2 | SAM-F-017 | UC-03 |
| [SAM-F-018/019](#sam-f-018019) | Report views: student-wise, subject-wise, class-wise | Anupam | 2 | 2 | SAM-F-018, SAM-F-019 | UC-06 |
| [SAM-F-020](#sam-f-020) | Report export and print (CSV, PDF) | Anupam | 2 | 2 | SAM-F-020 | UC-06 |
| [SAM-SEC-004](#sam-sec-004) | Students see only their own records; assignment and ownership checks | Anupam | 1 | 2 | SAM-SEC-004 | UC-07 |
| [SAM-SEC-005](#sam-sec-005) | Audit Module: log administrative actions, including DENIED and FAILED | Anusha | 2 | 2 | SAM-SEC-005 | UC-05 |
| [SAM-NF-005](#sam-nf-005) | Backup and restore commands (backup_db, restore_db) with audit entry | Anmol | 1 | 2 | SAM-NF-005 | - |
| [SAM-NF-002/004](#sam-nf-002004) | Availability and data protection: restart policy, HTTPS and secure cookies via Nginx | Anmol | 1 | 2 | SAM-NF-002, SAM-NF-004 | - |
| [SAM-NF-001](#sam-nf-001) | Report performance: indexes, aggregation in the DB, pagination | Anupriya | 1 | 2 | SAM-NF-001 | UC-06 |
| [SAM-NF-006/007](#sam-nf-006007) | Maintainability and scalability: module structure, lint, seeded-data load check | Anusha | 1 | 2 | SAM-NF-006, SAM-NF-007 | - |
| [TEST-02](#test-02) | Test cases and execution: Generate Reports (UC-06) and subjects/assignments (SAM-F-008, 009) | Anmol | 3 | 2 | SAM-F-008, 009, 018 to 020 | UC-06 |
| [TEST-04](#test-04) | Test cases and execution: View Percentage, View History (UC-03, UC-07); test data, RTM upkeep, metrics and summary report | Anusha | 5 | 2 | SAM-F-015 to 017, SAM-SEC-004 | UC-03, UC-07 |
| [TEST-05](#test-05) | Non-functional tests (TC-Perf-01, TC-Load-01, TC-UX-01, TC-Maint-01, TC-Reliability-01, TC-Recovery-01): each member takes areas they did not build; assign in Project Plan | Anupriya | 1 | 2 | SAM-NF-001 to 007 | - |
| [DOC-01](#doc-01) | Update STP: add SAM-F-008, 009, 014 to Sections 3 and 13; Docker, SonarCloud, Bandit, coverage.py in Section 6; TC-Att-03/04 steps | Anupriya | 1 | 2 | - | - |
| [DOC-02](#doc-02) | Update SRS wording for time slot (SAM-F-012, 013, UC-01); update README to match SAD | Anupam | 1 | 2 | SAM-F-012, 013 | UC-01 |
| [DOC-03](#doc-03) | Record Sprint 1 (1 min) and Sprint 2 (2 min) videos; upload to repo; document deviations from SRS/SAD/STP | Anupam | 1 | 2 | - | - |
| [TEST-REPORTS](#test-reports) | Unit test, code coverage and branch coverage reports | Anusha | 2 | 2 | all | all |
| [SYS-VAL](#sys-val) | System validation report and maintenance plan | Anupriya | 2 | 2 | all | UC-01 to UC-07 |
| [USER-STORIES](#user-stories) | Backlog as user stories with acceptance criteria | Anupam | 1 | 2 | all | all |
| [AGILE](#agile) | Scrum roles, ceremonies, estimation and sprint records | Anmol | 1 | 2 | - | - |

Sprint 1: 18 stories, 27 points. Sprint 2: 18 stories, 28 points, plus 4 stories
(6 points) for the final test reports and the process records.

## Stories

### SETUP-01

**Django skeleton, data model, migrations and seed script** · Anmol · 2 points · Sprint 1

> As a developer on the team, I want a Django project with the data model, migrations and sample data, so that every member can build their module on the same models and test with the same data.

Acceptance criteria:

- `python manage.py migrate` builds the database from an empty start
- `seed_data` creates an admin, two faculty, eight students, two classes, three subjects and time slots
- The models match the data model in SAD 4.1.1

Requirement Foundation (SAD Figure 4.1) · use case - · test cases TC-Maint-01 · source: SAD Table 2 #3

### SETUP-02

**Dockerfile, docker-compose and Nginx environment** · Anmol · 2 points · Sprint 1

> As a developer on the team, I want one command that starts Nginx, Django and MySQL the same way on every laptop, so that nobody loses time to "works on my machine" differences.

Acceptance criteria:

- `docker compose up --build` starts Nginx (HTTPS), Django (gunicorn) and MySQL 8.0
- https://localhost/ shows the login page; plain HTTP redirects to HTTPS
- Each container restarts on its own if it stops

Requirement SAM-NF-002, SAM-NF-004 · use case - · test cases TC-Reliability-01 · source: SAD Table 2 #4

### SETUP-03

**GitHub Actions pipeline: tests and coverage, Bandit, SonarCloud, image build** · Anupriya · 2 points · Sprint 1

> As a QA lead, I want every pull request checked automatically before it can be merged, so that broken or insecure code never reaches main.

Acceptance criteria:

- CI runs ruff, Django checks, the migration check, all tests on MySQL 8.0 and Bandit on every pull request
- CI fails when coverage drops below 85%
- The Docker image builds; on main it is published

Requirement SAM-NF-006 · use case - · test cases TC-Maint-01 · source: SAD Table 2 #15

### SAM-F-001

**Login with username and password** · Anupam · 1 point · Sprint 1

> As an user of SAMS (admin, faculty or student), I want to log in with my username and password, so that only I can reach my pages.

Acceptance criteria:

- Valid credentials log the user in
- Each role lands on its own dashboard

Requirement SAM-F-001 · use case UC-04 · test cases TC-Auth-01, ST-01 · source: SAD #8

### SAM-F-002/003

**Reject invalid login; role-based redirect (Admin, Faculty, Student)** · Anupam · 1 point · Sprint 1

> As an user of SAMS, I want a clear message when my login is wrong, and to land on the pages for my role, so that I know what went wrong and I only see what my role allows.

Acceptance criteria:

- A wrong username or password shows "Wrong username or password" and does not log in
- Admin, faculty and student each land on their own dashboard
- A user opening another role's page gets 403

Requirement SAM-F-002, SAM-F-003 · use case UC-04 · test cases TC-Auth-02, TC-Auth-03, ST-01, ST-02 · source: SAD #8

### SAM-F-004

**Add student** · Anusha · 1 point · Sprint 1

> As an administrator, I want to add a new student with their SRN, name, email and class, so that they can log in and their attendance can be recorded.

Acceptance criteria:

- The student is saved and listed
- A login is created with the SRN as username
- A duplicate SRN is refused with a message

Requirement SAM-F-004 · use case UC-04 · test cases TC-Student-01, ST-06 · source: SAD #16

### SAM-F-005/006

**Update and search student; deactivate instead of delete** · Anusha · 1 point · Sprint 1

> As an administrator, I want to find a student by SRN or name, correct their details, and deactivate them when they leave, so that the records stay right and their attendance history is never lost.

Acceptance criteria:

- Search by part of the SRN or name lists only matching students
- Edits are saved
- Deactivating hides the student and blocks their login, but keeps their history (ADR-003)

Requirement SAM-F-005, SAM-F-006 · use case UC-04 · test cases TC-Student-02, TC-Student-03, ST-07, ST-08 · source: SAD #16

### SAM-F-007

**Manage faculty** · Anusha · 1 point · Sprint 1

> As an administrator, I want to add, edit and deactivate faculty members with their logins, so that the right people can mark attendance.

Acceptance criteria:

- A new faculty member is listed and can log in
- Edits are saved; deactivating blocks the login

Requirement SAM-F-007 · use case UC-04 · test cases TC-Faculty-01, ST-09 · source: SAD #17

### SAM-F-008

**Manage subjects and time slots** · Anupriya · 1 point · Sprint 1

> As an administrator, I want to add and edit subjects and the one-hour time slots, so that attendance can be taken per subject and per hour.

Acceptance criteria:

- Subjects with code, name and semester can be added and edited
- Time slots with start and end times can be added and edited
- Duplicate codes are refused

Requirement SAM-F-008 · use case UC-04 · test cases TC-Subject-01, ST-10 · source: SAD #14

### SAM-F-009

**Assign subjects to faculty** · Anupriya · 1 point · Sprint 1

> As an administrator, I want to assign a subject and class to a faculty member, so that each faculty member can mark only what they teach.

Acceptance criteria:

- The assignment is listed
- It appears on the faculty member's dashboard and attendance list
- An assignment can be removed

Requirement SAM-F-009 · use case UC-04 · test cases TC-Subject-02, ST-11 · source: SAD #14

### SAM-NF-003

**Base templates and role dashboards** · Anusha · 2 points · Sprint 1

> As an user of SAMS, I want a simple, consistent page layout with a dashboard for my role, so that I can find every task in one or two clicks.

Acceptance criteria:

- Every page has a title, a link home and a logout button
- Each role's dashboard links to all its tasks
- Form fields have labels and errors are in plain words

Requirement SAM-NF-003 · use case - · test cases TC-UX-01, ST-31 · source: SAD #19

### SAM-SEC-001/002

**Default-deny access control: login required, role boundaries** · Anupam · 1 point · Sprint 1

> As an administrator responsible for the data, I want every page to require a login and each role to reach only its own pages, so that no one sees or changes data they shouldn't.

Acceptance criteria:

- Any page opened without a login redirects to the login page
- A student or faculty member opening admin pages gets 403

Requirement SAM-SEC-001, SAM-SEC-002 · use case UC-04 · test cases TC-SEC-01, TC-SEC-02, ST-03, ST-04 · source: SAD #9

### SAM-SEC-003

**Password hashing and login lockout (django-axes)** · Anupam · 1 point · Sprint 1

> As an administrator responsible for the data, I want passwords stored hashed and accounts locked after repeated wrong passwords, so that stolen data or guessing can't reveal or break into accounts.

Acceptance criteria:

- Passwords are stored only as hashes
- After 5 failed logins the account is locked for 15 minutes (HTTP 429)
- Every failed login is in the audit log

Requirement SAM-SEC-003 · use case UC-04 · test cases TC-SEC-03, ST-05 · source: SAD #10

### SAM-F-010

**Select class and subject** · Anmol · 1 point · Sprint 1

> As a faculty member, I want to pick one of my assigned classes and subjects before marking, so that I mark the right class.

Acceptance criteria:

- Only my assigned class and subject pairs are offered
- Typing the address of another pair is refused

Requirement SAM-F-010 · use case UC-02 · test cases TC-Att-01, ST-12, ST-16 · source: SAD #1

### SAM-F-011

**Mark each student Present or Absent (marking sheet, one or more time slots)** · Anmol · 1 point · Sprint 1

> As a faculty member, I want a sheet of my class where I mark each student Present or Absent for one or more hours, so that I can take attendance in under a minute.

Acceptance criteria:

- Every active student of the class is listed, Present by default
- One or more time slots can be chosen
- Saving confirms how many students and slots were saved

Requirement SAM-F-011 · use case UC-01 · test cases TC-Att-02, ST-13 · source: SAD #1

### SAM-F-012/013

**Store attendance in one transaction; reject duplicates per student, subject, date, time slot** · Anmol · 1 point · Sprint 1

> As a faculty member, I want attendance saved completely or not at all, and never twice for the same hour, so that the records are always correct.

Acceptance criteria:

- Each record holds student, subject, date, time slot, status and who marked it
- All rows of a sheet are saved together
- Marking the same class, subject, date and slot again is refused
- A future date is refused

Requirement SAM-F-012, SAM-F-013 · use case UC-01 · test cases TC-Att-03, TC-Att-04, ST-13, ST-14, ST-15 · source: SAD #1

### SAM-F-014

**Modify attendance with a reason** · Anmol · 1 point · Sprint 2

> As a faculty member, I want to correct attendance I already saved, giving a reason, so that mistakes can be fixed and every change is accounted for.

Acceptance criteria:

- Only the assigned faculty member can modify
- A reason of at least a few words is required
- The change and its reason are written to the audit log

Requirement SAM-F-014 · use case UC-01 · test cases TC-Att-05, ST-17, ST-18 · source: SAD #2

### SAM-F-015

**Calculate attendance percentage per subject** · Anupriya · 1 point · Sprint 2

> As a student, I want to see my attendance percentage in each subject, so that I know where I stand before exams.

Acceptance criteria:

- Percentage = classes attended / classes held, per subject
- A subject with no classes yet shows no percentage instead of an error

Requirement SAM-F-015 · use case UC-03 · test cases TC-Calc-01, ST-19 · source: SAD #11

### SAM-F-016

**Student attendance history (newest first)** · Anupriya · 1 point · Sprint 2

> As a student, I want to see every class I was marked for, newest first, so that I can check any day's record.

Acceptance criteria:

- Each entry shows date, time slot, subject and status
- Newest first
- Only my own records are shown

Requirement SAM-F-016 · use case UC-07 · test cases TC-View-01, ST-21 · source: SAD #13

### SAM-F-017

**Threshold setting and low-attendance flags** · Anupriya · 2 points · Sprint 2

> As an administrator, I want to set the minimum attendance percentage, and have students below it flagged, so that students and faculty act before it is too late.

Acceptance criteria:

- The admin sets the threshold (75% by default)
- A student below it sees a warning on their dashboard
- Faculty see the students below it in their classes
- Reports mark low percentages in red

Requirement SAM-F-017 · use case UC-03 · test cases TC-Alert-01, ST-20 · source: SAD #12

### SAM-F-018/019

**Report views: student-wise, subject-wise, class-wise** · Anupam · 2 points · Sprint 2

> As a faculty member or administrator, I want student-wise, subject-wise and class-wise attendance reports for a date range, so that I can review attendance at any level.

Acceptance criteria:

- Each report shows classes held, attended and % per row
- A date range narrows the report
- Faculty see only their own subjects; the admin sees all

Requirement SAM-F-018, SAM-F-019 · use case UC-06 · test cases TC-Report-01, TC-Report-02, ST-23, ST-24 · source: SAD #6

### SAM-F-020

**Report export and print (CSV, PDF)** · Anupam · 2 points · Sprint 2

> As a faculty member or administrator, I want to download a report as CSV or PDF, or print it, so that I can share it or keep it on file.

Acceptance criteria:

- CSV and PDF contain every row, not just the page shown
- The print view hides the navigation

Requirement SAM-F-020 · use case UC-06 · test cases TC-Report-03, ST-25, ST-26 · source: SAD #7

### SAM-SEC-004

**Students see only their own records; assignment and ownership checks** · Anupam · 1 point · Sprint 2

> As a student, I want my attendance to be visible only to me, my faculty and the admin, so that my records stay private.

Acceptance criteria:

- A student opening another student's history or report gets 403
- A faculty member opening a class or subject they don't teach is refused

Requirement SAM-SEC-004 · use case UC-07 · test cases TC-SEC-04, ST-16, ST-22 · source: SAD #9

### SAM-SEC-005

**Audit Module: log administrative actions, including DENIED and FAILED** · Anusha · 2 points · Sprint 2

> As an administrator, I want a log of every admin change, refused page and failed login, so that I can see who did what and spot misuse.

Acceptance criteria:

- Entries show time, user, action and outcome (SUCCESS, DENIED, FAILED)
- Entries can't be edited or deleted
- The log can be filtered by outcome and searched

Requirement SAM-SEC-005 · use case UC-05 · test cases TC-SEC-05, ST-18, ST-27 · source: SAD #18

### SAM-NF-005

**Backup and restore commands (backup_db, restore_db) with audit entry** · Anmol · 1 point · Sprint 2

> As an administrator, I want to back up the database and restore it, so that no attendance is lost if something goes wrong.

Acceptance criteria:

- `backup_db` writes a compressed backup and keeps the last N
- `restore_db` asks for confirmation, then restores everything
- Both are written to the audit log

Requirement SAM-NF-005 · use case - · test cases TC-Recovery-01 · source: SAD #5

### SAM-NF-002/004

**Availability and data protection: restart policy, HTTPS and secure cookies via Nginx** · Anmol · 1 point · Sprint 2

> As an administrator responsible for the data, I want the system to stay up and all traffic to be encrypted, so that users can rely on it and nobody can read data in transit.

Acceptance criteria:

- Containers restart on their own; /health/ returns 503 when the database is down
- All traffic is HTTPS
- Session cookies are Secure, HttpOnly and expire after 30 idle minutes

Requirement SAM-NF-002, SAM-NF-004 · use case - · test cases TC-Reliability-01, TC-Sec-01, ST-29, ST-30 · source: Not itemised in SAD Table 2

### SAM-NF-001

**Report performance: indexes, aggregation in the DB, pagination** · Anupriya · 1 point · Sprint 2

> As a faculty member or administrator, I want reports to open quickly even with a full term of data, so that I don't wait for them.

Acceptance criteria:

- Every main page and report answers within 3 seconds with a term of data
- Reports are paged on screen; downloads have every row

Requirement SAM-NF-001 · use case UC-06 · test cases TC-Perf-01, ST-28 · source: SAD 4.6 (open item)

### SAM-NF-006/007

**Maintainability and scalability: module structure, lint, seeded-data load check** · Anusha · 1 point · Sprint 2

> As a developer on the team, I want clean, modular code that holds up with many users, so that the system is easy to change and doesn't slow down in use.

Acceptance criteria:

- One Django app per module; lint clean; no function above complexity 10
- 20 users at once get pages without errors within 3 seconds

Requirement SAM-NF-006, SAM-NF-007 · use case - · test cases TC-Maint-01, TC-Load-01, ST-32 · source: Not itemised in SAD Table 2

### TEST-01

**Test cases and execution: Mark Attendance, Select Class and Subject (UC-01, UC-02) and attendance modification (SAM-F-014)** · Anupam · 3 points · Sprint 1

> As a QA lead, I want automated test cases for marking, selecting and modifying attendance, so that UC-01 and UC-02 are proven to work on every change.

Acceptance criteria:

- TC-Att-01 to TC-Att-05 automated and passing
- They run in CI on every pull request

Requirement SAM-F-010 to 014 · use case UC-01, UC-02 · test cases TC-Att-01 to TC-Att-05 · source: SAD Table 1; STP 9

### TEST-02

**Test cases and execution: Generate Reports (UC-06) and subjects/assignments (SAM-F-008, 009)** · Anmol · 3 points · Sprint 2

> As a QA lead, I want automated test cases for reports and subject management, so that UC-06 is proven to work on every change.

Acceptance criteria:

- TC-Report-01 to 03 and TC-Subject-01, 02 automated and passing

Requirement SAM-F-008, 009, 018 to 020 · use case UC-06 · test cases TC-Report-01 to 03, TC-Subject-01, 02 · source: SAD Table 1; STP 9

### TEST-03

**Test cases and execution: Manage User Access, Log Administrative Action (UC-04, UC-05); quality gates and PR review rules** · Anupriya · 4 points · Sprint 1

> As a QA lead, I want automated test cases for user access and the audit log, and quality gates on every pull request, so that UC-04 and UC-05 are proven and no unreviewed code is merged.

Acceptance criteria:

- UC-04 and UC-05 test cases automated and passing
- Pull requests need green CI and a reviewer's approval (CONTRIBUTING.md)

Requirement SAM-F-001 to 007, SAM-SEC-001 to 005 · use case UC-04, UC-05 · test cases TC-Student-01 to 03, TC-Faculty-01, TC-SEC-02, TC-SEC-05 · source: SAD Table 1; STP 9

### TEST-04

**Test cases and execution: View Percentage, View History (UC-03, UC-07); test data, RTM upkeep, metrics and summary report** · Anusha · 5 points · Sprint 2

> As a QA lead, I want automated test cases for the student views, plus the test data, RTM and test summary, so that UC-03 and UC-07 are proven and the team can see test status at a glance.

Acceptance criteria:

- TC-Calc-01, TC-Alert-01, TC-View-01, TC-SEC-04 automated and passing
- docs/testing/ has the RTM, test data and test summary

Requirement SAM-F-015 to 017, SAM-SEC-004 · use case UC-03, UC-07 · test cases TC-Calc-01, TC-Alert-01, TC-View-01, TC-SEC-04 · source: SAD Table 1; STP 9

### TEST-05

**Non-functional tests (TC-Perf-01, TC-Load-01, TC-UX-01, TC-Maint-01, TC-Reliability-01, TC-Recovery-01): each member takes areas they did not build; assign in Project Plan** · Anupriya · 1 point · Sprint 2

> As a QA lead, I want the non-functional requirements tested by someone other than their builder, so that the targets in the SRS are proven independently.

Acceptance criteria:

- TC-Perf-01, TC-Load-01, TC-UX-01, TC-Maint-01, TC-Reliability-01, TC-Recovery-01 automated and passing

Requirement SAM-NF-001 to 007 · use case - · test cases TC-Perf-01, TC-Load-01, TC-UX-01, TC-Maint-01, TC-Reliability-01, TC-Recovery-01 · source: SAD Table 3 (shared)

### DOC-01

**Update STP: add SAM-F-008, 009, 014 to Sections 3 and 13; Docker, SonarCloud, Bandit, coverage.py in Section 6; TC-Att-03/04 steps** · Anupriya · 1 point · Sprint 2

> As an evaluator, I want the test plan to match what was built and tested, so that I can trace every requirement to its tests.

Acceptance criteria:

- STP v1.1 covers SAM-F-008, 009 and 014
- Section 6 lists the tools actually used
- Appendix A lists every test case

Requirement - · use case - · test cases - · source: SAD 4.6 next steps

### DOC-02

**Update SRS wording for time slot (SAM-F-012, 013, UC-01); update README to match SAD** · Anupam · 1 point · Sprint 2

> As an evaluator, I want the SRS and README to match the system as built, so that nothing in the documents contradicts the demo.

Acceptance criteria:

- SRS v1.1 states attendance per time slot
- README describes the architecture, setup and documents

Requirement SAM-F-012, 013 · use case UC-01 · test cases - · source: SAD 4.6 next steps

### DOC-03

**Record Sprint 1 (1 min) and Sprint 2 (2 min) videos; upload to repo; document deviations from SRS/SAD/STP** · Anupam · 1 point · Sprint 2

> As an evaluator, I want a short video of each sprint's working product and a list of deviations, so that I can see what each sprint delivered and why it differs from the plan.

Acceptance criteria:

- docs/videos/ has the Sprint 1 (1 min) and Sprint 2 (2 min) videos
- docs/DEVIATIONS.md explains every deviation

Requirement - · use case - · test cases - · source: Deliverables Part-2

### TEST-REPORTS

**Unit test, code coverage and branch coverage reports** · Anusha · 2 points · Sprint 2

> As an evaluator, I want the unit test results and the code and branch coverage of v1.0 in the docs folder, so that I can check the test results without running anything.

Acceptance criteria:

- docs/reports/unit-tests/ has the results by test file with RTM test case IDs, an HTML report and JUnit XML
- docs/reports/coverage/ has line and branch coverage by module, the untested lines and branches, the HTML report and XML

Requirement all · use case all · test cases all · source: STP Section 8 (test deliverables) and Section 14 (metrics)

### SYS-VAL

**System validation report and maintenance plan** · Anupriya · 2 points · Sprint 2

> As an evaluator, I want the finished system validated end to end like a real user would use it, and a plan for maintaining it, so that I know v1.0 works as a whole and how it will be looked after.

Acceptance criteria:

- Black-box system test cases for all 7 use cases, the security checks and the non-functional targets, run on a live server
- Results in the course's test case template with actual results
- docs/maintenance-plan.md exists

Requirement all · use case UC-01 to UC-07 · test cases ST-01 to ST-32 · source: STP Section 5 and 5.1; guidelines stage System Validation

### USER-STORIES

**Backlog as user stories with acceptance criteria** · Anupam · 1 point · Sprint 2

> As a Product Owner, I want every backlog item written as a user story with acceptance criteria, so that the team builds from the user's point of view and knows when an item is done.

Acceptance criteria:

- Every backlog issue starts with its user story and acceptance criteria
- docs/user-stories.md maps each story to its requirements, use cases, test cases, owner, points and sprint

Requirement all · use case all · test cases - · source: Guidelines: GitHub used for user stories and backlog

### AGILE

**Scrum roles, ceremonies, estimation and sprint records** · Anmol · 1 point · Sprint 2

> As a Scrum Master, I want our Scrum roles, events, estimates, velocity and blockers written down, so that anyone can see how the team ran its sprints.

Acceptance criteria:

- docs/agile-process.md names the Product Owner, Scrum Master and Development Team
- It records the sprint plans, story points, velocity, blockers and retrospective points

Requirement - · use case - · test cases - · source: Guidelines: Agile methodology only
