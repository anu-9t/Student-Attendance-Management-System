# How we ran the project (Scrum)

Owner: Anmol Vyas (Scrum Master). The guidelines ask for "Agile methodology only"; we used Scrum with two one-week
sprints, tracked on GitHub. The backlog itself, as user stories, is in [user-stories.md](user-stories.md).

## Roles

| Scrum role | Who | What it meant in this project |
|---|---|---|
| Product Owner | Anupam Rajesh Tiwari | Turned the SRS into the backlog on the SAMS Backlog board; set the priorities, story points and the sprint of each story; accepted finished work by merging its pull request (repository owner) |
| Scrum Master | Anmol Vyas | Ran the sprint calls and the check-ins in the team group; kept the board in step with the work; chased blockers until they were cleared; ran the sprint reviews and retrospectives |
| Development Team | Anmol Vyas, Anupam Rajesh Tiwari, Anupriya, Anusha G | Built, tested and reviewed the stories. Everyone owns stories in both sprints (SAD Table 1) |

Inside the Development Team, the test roles from STP Section 9 also apply: Anupriya is QA Lead (quality gates, CI,
defect triage) and Anusha G is Test Engineer (test data, RTM, test reports). Every pull request is reviewed by a fixed
partner who did not write it: Anupam and Anmol review each other, Anusha and Anupriya review each other (SAD Table 3).

## Events

| Event | When | What happened |
|---|---|---|
| Backlog creation | Before Sprint 1 | Product Owner wrote one backlog item per SRS requirement (two closely related requirements share one), plus set-up, test and documentation items from SAD Table 1; labels, owners, story points |
| Sprint planning | Start of each sprint (19 Oct, 26 Oct) | Team chose the stories for the sprint from the backlog and the dependencies between them (for example login and the data model before attendance); each story went into that sprint's milestone |
| Check-ins | During each sprint | Short updates in the team group: what was done, what's next, what's blocking. The board's In Progress column shows who is on what |
| Sprint review | End of each sprint (23 Oct, 30 Oct) | The working product was shown: a 1-minute (Sprint 1) and 2-minute (Sprint 2) video in [docs/videos/](videos/), and the presentation to the course instructor |
| Retrospective | After each sprint | What to keep and what to change; the changes are listed below |

## Estimation

Story points measure relative effort, agreed by the team at planning; the Product Owner had the final say.

| Points | Meant | Example |
|---|---|---|
| 1 | One form or view, or one rule, with its tests | SAM-F-004 Add student |
| 2 | A small module or a piece of infrastructure | SAM-F-017 Threshold and alerts; SETUP-02 Docker |
| 3 to 5 | A whole use case's test cases and their execution, or several | TEST-04 (UC-03, UC-07, test data, RTM, summary report) |

## Sprints

| | Sprint 1 (19 to 23 Oct) | Sprint 2 (26 to 30 Oct) |
|---|---|---|
| Goal | A working core: set-up, login and access control, student, faculty and subject management, marking attendance | Everything else: percentage, history, alerts, modification, reports, audit, backup, the non-functional targets; documents v1.1 |
| Stories planned / done | 18 / 18 | 18 / 18, plus 4 added for the final reports and these records |
| Story points planned / done (velocity) | 27 / 27 | 28 / 28 (34 with the 4 added stories) |
| Pull requests merged | 18 | 22 |
| End | Tag `sprint-1`, milestone closed, 1-minute video | Tags `sprint-2` and `v1.0`, milestone closed, 2-minute video |

Story points per member (both sprints, including the 4 added stories): Anupriya 17, Anupam 15, Anusha 15, Anmol 14.

## Definition of Done

A story is done when all of these hold:

1. Every acceptance criterion in its user story is met.
2. Its test cases are automated and pass; the RTM row is updated.
3. CI is green: ruff, Django checks, migrations, all tests on MySQL 8.0, coverage at least 85%, Bandit, Docker build.
4. The review partner has approved the pull request.
5. The Product Owner has merged it, and the card is in Done.

## Blockers and how they were cleared

| Blocker | Sprint | Cleared by |
|---|---|---|
| The test suite was slow because of password hashing in every test | 1 | A fast test-only password hasher in `tests/conftest.py`; the suite runs in about 30 seconds |
| Board cards didn't always move to Done when a pull request closed its issue | 1 and 2 | The board is synced after each day's merges |
| The 20-user load test (TC-Load-01) failed with "table is locked" on SQLite | 2 | Sessions in signed cookies for that test, and users logged in before timing starts; the timings are noted as pessimistic |
| The new lint gate found unsorted imports and other style issues | 2 | Fixed in the maintainability story (SAM-NF-006/007) before it was merged |
| The health check said "ok" even with the database down | 2 | `/health/` now queries the database and returns 503 (found by TC-Reliability-01) |
| The audit log's outcome filter had no label for screen readers | 2 | Label added (found by TC-UX-01) |
| A restore removed the audit entry of the backup it restored | 2 | The backup writes its audit entry before taking the dump |
| On Windows checkouts the Nginx start script got Windows line endings and Nginx didn't start; the admin dashboard had no link to Subjects | 2 | `.gitattributes` keeps scripts in LF; two dashboard cards added (#83) |

## Retrospective: what we changed

| After | Keep | Change |
|---|---|---|
| Sprint 1 | One branch and one pull request per story; fixed review partners; CI on every pull request; the fast test settings | Add a lint and complexity gate to CI; sync the board after each day's merges |
| Sprint 2 | Writing the non-functional tests as code, so they run in CI | Non-functional tests by someone other than the builder (shared branch, one commit per owner); test the app on Windows as well as Mac before a demo |
