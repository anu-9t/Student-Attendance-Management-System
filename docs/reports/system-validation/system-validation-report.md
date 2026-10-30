# System validation report

Owner: Anupriya (QA Lead). Guidelines stage "System Validation: validation report + maintenance plan"; STP Section 5
(system testing) and Section 5.1 (security validation). The maintenance plan is [docs/maintenance-plan.md](../../maintenance-plan.md).

**Result: 32 of 32 system test cases passed. All 7 use cases and 30 of the 32 requirements
were validated on the running system; the other 2 are validated by their own test cases in the unit test run.**

## What was tested, and how

| | |
|---|---|
| System under test | `main` at `a5c5066`, the frozen Sprint 2 code (tags `sprint-2`, `v1.0`) |
| Run | 30 Oct 2026, 18:30 IST |
| Server | gunicorn, 2 workers, over HTTPS (self-signed certificate), `DJANGO_DEBUG=0` (production settings: HTTPS-only cookies, HTTPS redirect, safe headers); fresh SQLite database with `seed_data` |
| Client | `tools/system_validation.py`: logs in and fills the real forms over HTTPS like a browser, following redirects and keeping cookies; it imports nothing from the application |
| Method | Black-box, usage-driven: each case is a user task from the SRS use cases, checked only by what the user sees (pages, messages, files, status codes). White-box testing is the [unit test run](../unit-tests/unit-test-report.md) with [code](../coverage/code-coverage-report.md) and [branch coverage](../coverage/branch-coverage-report.md) |
| Not in this run | MySQL and the Nginx container. MySQL is exercised by CI on every pull request (same tests on MySQL 8.0); the Nginx headers and HTTPS redirect are checked by `tests/test_data_protection.py`, and the full Docker stack is shown in the Sprint 2 video |

The cases run in order and build on each other (ST-06 adds the student that ST-07 and ST-08 search and deactivate;
ST-13 marks the attendance that ST-14 to ST-26 use), the way a real day of use would.

## Use cases validated

| Use case | System test cases | Result |
|---|---|---|
| UC-01 Mark Attendance | ST-13, ST-14, ST-15, ST-17, ST-18 | Pass |
| UC-02 Select Class and Subject | ST-12, ST-16 | Pass |
| UC-03 View Attendance Percentage | ST-19, ST-20 | Pass |
| UC-04 Manage User Access | ST-01, ST-02, ST-03, ST-04, ST-05, ST-06, ST-07, ST-08, ST-09, ST-10, ST-11 | Pass |
| UC-05 Log Administrative Action | ST-18, ST-27 | Pass |
| UC-06 Generate Reports | ST-23, ST-24, ST-25, ST-26 | Pass |
| UC-07 View Attendance History | ST-21, ST-22 | Pass |

## Requirements validated

| Requirement | System test cases |
|---|---|
| SAM-F-001 | ST-01 |
| SAM-F-002 | ST-02 |
| SAM-F-003 | ST-01 |
| SAM-F-004 | ST-06 |
| SAM-F-005 | ST-08 |
| SAM-F-006 | ST-07 |
| SAM-F-007 | ST-09 |
| SAM-F-008 | ST-10 |
| SAM-F-009 | ST-11 |
| SAM-F-010 | ST-12 |
| SAM-F-011 | ST-13 |
| SAM-F-012 | ST-13, ST-15 |
| SAM-F-013 | ST-14 |
| SAM-F-014 | ST-17, ST-18 |
| SAM-F-015 | ST-19 |
| SAM-F-016 | ST-21 |
| SAM-F-017 | ST-20 |
| SAM-F-018 | ST-24 |
| SAM-F-019 | ST-23, ST-24 |
| SAM-F-020 | ST-25, ST-26 |
| SAM-NF-001 | ST-28 |
| SAM-NF-002 | ST-29 |
| SAM-NF-003 | ST-31 |
| SAM-NF-004 | ST-30 |
| SAM-NF-005 | not run at system level: TC-Recovery-01 (backup, damage, restore; unit test run) |
| SAM-NF-006 | not run at system level: TC-Maint-01 (lint, complexity, module structure; unit test run) |
| SAM-NF-007 | ST-32 |
| SAM-SEC-001 | ST-03 |
| SAM-SEC-002 | ST-04, ST-16 |
| SAM-SEC-003 | ST-05 |
| SAM-SEC-004 | ST-16, ST-22 |
| SAM-SEC-005 | ST-18, ST-27 |

## Test cases

Columns follow the course's test case template (Test Case ID, Module, Description, Pre-conditions, Test Steps,
Test Data, Expected Result, Actual Result, Test Result). The actual results are what the run recorded.

| Test Case ID | Module | Test case description | Pre-conditions | Test steps | Test data | Expected result | Actual result | Test result |
|---|---|---|---|---|---|---|---|---|
| ST-01 | Login (accounts) | Valid login takes each role to its own dashboard | Server running with seed_data | 1. Open /login/<br>2. Enter username and password<br>3. Submit | admin / faculty1 / student1, password Sams@12345 | Admin, Faculty and Student dashboards respectively | admin landed on /dashboard/admin/ (dashboard shown); faculty1 landed on /dashboard/faculty/ (dashboard shown); student1 landed on /dashboard/student/ (dashboard shown) | Pass |
| ST-02 | Login (accounts) | Wrong password is refused with a message | Server running | 1. Open /login/<br>2. Enter a wrong password<br>3. Submit | student1 / WrongPass1 | Login page shown again with an error; no session | Stayed on /login/; error message shown; session cookie not set | Pass |
| ST-03 | Access control | Every page needs a login | Not logged in | 1. Open each protected URL without logging in | /dashboard/, /students/, /attendance/select/, /reports/, /audit/, /percentage/ | Each request is redirected to /login/ | /dashboard/ -> 302 /login/; /students/ -> 302 /login/; /attendance/select/ -> 302 /login/; /reports/ -> 302 /login/; /audit/ -> 302 /login/; /percentage/ -> 302 /login/ | Pass |
| ST-04 | Access control | Each role reaches only its own pages | Logged in as student1, then as faculty1 | 1. As a student, open admin and faculty pages<br>2. As faculty, open admin pages | /students/, /audit/, /attendance/select/, /subjects/ | 403 Forbidden for every page outside the role | student /students/ -> 403; student /audit/ -> 403; student /attendance/select/ -> 403; student /subjects/ -> 403; faculty /students/ -> 403; faculty /audit/ -> 403; faculty /subjects/ -> 403 | Pass |
| ST-05 | Login lockout | Account locks after 5 failed logins | faculty2 not used in this run | 1. Submit 5 wrong passwords for faculty2<br>2. Try the correct password | faculty2 / Wrong1234 (x5), then Sams@12345 | 6th attempt refused with HTTP 429 and a lockout message, even with the right password | After 5 failures the correct password returned HTTP 429 with the lockout page | Pass |
| ST-06 | Student management | Admin adds a student, who can then log in | Logged in as admin; class CSE-5A exists | 1. Students -> Add<br>2. Fill the form<br>3. Save<br>4. Log in as the new student | SRN PES2UG24CS200, name Test Student, test@example.com, CSE-5A, password Welcome@123 | Student listed; the new login reaches the student dashboard | Saved (Added Test Student (PES2UG24CS200).); listed: True; new login reached the student dashboard | Pass |
| ST-07 | Student management | Search students by SRN or name | ST-06 done | 1. Students<br>2. Search by part of the SRN, then by name | q=CS200, q=test student | Only matching students listed | q=CS200 listed 1 SRN(s) incl. PES2UG24CS200; q=test student found it: True | Pass |
| ST-08 | Student management | Edit, then deactivate a student (never deleted) | ST-06 done | 1. Edit the student's name<br>2. Deactivate the student<br>3. List, then list with 'show all' | Name changed to Test Student Two | Name updated; hidden from the active list; still shown under 'all' | renamed: True; hidden from active list: True; still in 'all': True | Pass |
| ST-09 | Faculty management | Admin adds a faculty member | Logged in as admin | 1. Faculty -> Add<br>2. Fill the form<br>3. Save | F900, Test Faculty, CSE | Faculty member listed | Added Test Faculty.; listed: True | Pass |
| ST-10 | Subject management | Admin adds a subject and a time slot | Logged in as admin | 1. Subjects -> Add, save<br>2. Time slots -> Add, save | UE24CS399A Test Subject sem 5; slot 'Test slot' 18:00-19:00 | Both listed | subject listed: True; time slot listed: True | Pass |
| ST-11 | Subject assignment | Admin assigns a subject and class to a faculty member | ST-09 and ST-10 done | 1. Subject Assignments<br>2. Pick faculty, subject, class<br>3. Assign | Test Faculty, UE24CS399A, CSE-5A | Assignment listed | assignment listed: True | Pass |
| ST-12 | Select class (attendance) | Faculty sees only their assigned class/subject pairs | Logged in as faculty1 (teaches UE24CS341A to CSE-5A and CSE-5B) | 1. Mark Attendance<br>2. Read the list | - | Exactly the 2 assigned pairs; Computer Networks / DBMS not offered | 2 class/subject pairs offered; other faculty's subjects shown: False | Pass |
| ST-13 | Mark attendance | Faculty marks a class for one slot | Logged in as faculty1 | 1. Select CSE-5A / UE24CS341A<br>2. Pick today and slot 1<br>3. Mark the first student Absent, others Present<br>4. Save | today's date, first slot | Confirmation 'Saved attendance for N students, 1 slot' | Saved attendance for 4 students, 1 slot, on 30 Oct 2026. | Pass |
| ST-14 | Mark attendance | The same class, date and slot can't be saved twice | ST-13 done | 1. Open the same sheet<br>2. Same date and slot<br>3. Save | today, first slot | Refused with 'already saved'; nothing new stored | Attendance for Period 1 on 30 Oct 2026 is already saved. Nothing was saved this time; use Modify attendance to change it. | Pass |
| ST-15 | Mark attendance | A future date is refused | Logged in as faculty1 | 1. Open the sheet<br>2. Pick tomorrow<br>3. Save | tomorrow's date | Refused: attendance can't be marked for a future date | Attendance can't be marked for a future date. | Pass |
| ST-16 | Mark attendance | Faculty can't open a class or subject they don't teach | Logged in as faculty1 | 1. Type the URL of faculty2's class/subject sheet | /attendance/mark/<CSE-5A>/<UE24CS342A>/ | Refused (403 or 404); no sheet shown | HTTP 404 | Pass |
| ST-17 | Modify attendance | A correction without a reason is refused | ST-13 done | 1. Modify -> today, slot 1<br>2. Change a status<br>3. Save with an empty reason | reason '' | Refused: a reason is required; nothing changed | Please give a reason for the change (at least a few words). | Pass |
| ST-18 | Modify attendance | A correction with a reason is saved and logged | ST-13 done | 1. Modify -> today, slot 1<br>2. Change the absent student to Present<br>3. Reason given<br>4. Save<br>5. Admin opens the audit log | reason 'Medical certificate shown' | 'Updated 1 record'; audit log has the change and the reason | Updated 1 record.; audit entry with reason: True | Pass |
| ST-19 | Attendance percentage | Student sees their percentage per subject | ST-13: student1 marked; faculty marks one more slot absent for student1 | 1. Log in as student1<br>2. Open My Attendance | - | Percentage shown per subject, matching the marked classes | UE24CS341A shown as 50.0% (1 present of 2 classes) | Pass |
| ST-20 | Threshold and alerts | Admin sets the threshold; low students are warned | ST-19 done (student1 at 50% in UE24CS341A) | 1. Admin -> Attendance threshold -> 60 -> Save<br>2. student1 opens the dashboard<br>3. faculty1 opens the dashboard | threshold 60 | Saved; student1 sees a low-attendance warning; faculty1 sees student1 in the below-threshold list | Threshold set to 60%.; student warning: True; on faculty list: True | Pass |
| ST-21 | Attendance history | Student sees their history, newest first | ST-13 and ST-19 done | 1. Log in as student1<br>2. Open My History | - | Each marked class listed with date, slot, subject and status | 3 entries for UE24CS341A, statuses shown | Pass |
| ST-22 | Ownership | A student can't open another student's records | Logged in as student1 | 1. Type the URL of another student's history and report | /history/student/2/, /reports/student/2/ | Refused (403 or 404) | /history/student/2/ -> HTTP 403; /reports/student/2/ -> HTTP 403 | Pass |
| ST-23 | Reports | Subject-wise report for a date range | ST-13 done; logged in as faculty1 | 1. Reports -> subject report for CSE-5A / UE24CS341A<br>2. Enter a date range covering today | date_from = date_to = today | Every student of the class with classes held, attended and %, low ones marked | HTTP 200; 4 students listed with percentages | Pass |
| ST-24 | Reports | Student-wise and class-wise reports (admin) | ST-13 done; logged in as admin | 1. Reports -> search a student -> open<br>2. Reports -> class CSE-5A | q=PES2UG24CS091 | Both reports open with the marked data | student report: HTTP 200; class report: HTTP 200 | Pass |
| ST-25 | Report export | Download a report as CSV | ST-23 done | 1. Open the subject report<br>2. Download CSV | format=csv | A CSV file with a header row and one row per student | text/csv; charset=utf-8; attachment; filename="sams-ue24cs341a-cse-5a-subject-wise-report-20261030.csv"; 7 lines; header: UE24CS341A CSE-5A subject-wise report | Pass |
| ST-26 | Report export | Download a report as PDF; print view | ST-23 done | 1. Open the subject report<br>2. Download PDF<br>3. Check the print button and print styles | format=pdf | A valid PDF file; the page has a Print button and hides navigation when printed | application/pdf, 2409 bytes, starts with %PDF-: True; print view: True | Pass |
| ST-27 | Audit log | Admin actions, refusals and failed logins are logged | Earlier cases done (ST-02, ST-04, ST-06) | 1. Admin -> Audit Log<br>2. Filter by outcome | outcome = SUCCESS, DENIED, FAILED | Entries of all three kinds, with user and time | SUCCESS: 9 entries, DENIED: 8 entries, FAILED: 7 entries | Pass |
| ST-28 | Performance | Main pages answer within 3 seconds | Data from this run | 1. Open each main page as its role, timing each request | 16 pages, 3 roles | Every page under 3 s | 16 pages; slowest /reports/subject/1/1/?format=pdf at 75 ms; median 10 ms | Pass |
| ST-29 | Availability | Health check reports the server and database | Server running | 1. Open /health/ without logging in | - | HTTP 200 'ok' (503 if the database is down) | HTTP 200: {"status": "ok"} | Pass |
| ST-30 | Data protection | Session cookie is protected; logout ends the session | Production settings (DEBUG off) | 1. Log in, read the session cookie flags<br>2. Log out<br>3. Open the dashboard again | student1 | Cookie Secure, HttpOnly and SameSite; after logout the dashboard redirects to /login/ | session cookie flags {'Secure': True, 'HttpOnly': True, 'SameSite': True}; after logout /dashboard/ -> 302 /login/ | Pass |
| ST-31 | Usability | Every page has a title, a way home and a way out | Logged in as each role | 1. Open each role's main pages<br>2. Check page title, home link, Logout button | admin, faculty1, student1 | All present on every page | all pages have title, home and logout | Pass |
| ST-32 | Load | 20 users at once | Server with 2 gunicorn workers | 1. 20 users log in and open 5 pages each, at the same time | student1-8, faculty1, admin (repeated) | No errors; 95% of pages under 3 s | 20 users, 100 page views in 2.8 s; errors 0; median 124 ms, 95th percentile 147 ms | Pass |

## Security validation (STP 5.1)

ST-03, ST-04, ST-05, ST-16, ST-22, ST-27 and ST-30 are the security cases: login required everywhere, role
separation, lockout after 5 failures (HTTP 429), faculty limited to their own classes, students limited to their own
records, the audit trail of successes, refusals and failed logins, and the session cookie (Secure, HttpOnly,
SameSite) ending on logout. All passed.

## Defects

None found in this run. Defects found earlier in Sprint 2 testing, all fixed, are listed in the
[test summary](../../testing/test-summary.md).

## How to repeat this run

See the instructions at the top of `tools/system_validation.py`. It needs a fresh database each time, because
it adds a student and marks attendance. The raw results of this run are in
[system-validation-results.json](system-validation-results.json).
