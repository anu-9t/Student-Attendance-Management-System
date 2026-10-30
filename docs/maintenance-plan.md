# Maintenance plan

Owner: Anupriya (QA Lead), with the module owners from SAD Table 1. Guidelines stage "System Validation:
validation report + maintenance plan". Applies to SAMS v1.0 (`main` at `a5c5066`, tags `sprint-2`, `v1.0`), as
validated in the [system validation report](reports/system-validation/system-validation-report.md).

## Who looks after what

| Area | Owner | Reviewer |
|---|---|---|
| Attendance marking and modification, data model, Docker and Nginx, backup and restore | Anmol Vyas | Anupam |
| Login, access control, lockout, reports and export | Anupam Rajesh Tiwari | Anmol |
| Percentage, history, threshold and alerts, subjects and assignments, CI | Anupriya | Anusha |
| Students, faculty, audit log, dashboards and templates | Anusha G | Anupriya |
| Triage of every reported defect; test reports | Anupriya (QA Lead), Anusha (Test Engineer) | |
| Merging and releases | Anupam (repository owner) | |

## How a change is made

Every change, however small, goes the same way as during the sprints (`CONTRIBUTING.md`):

1. A GitHub issue on the SAMS Backlog board, labelled `bug`, `maintenance` or `enhancement`, with story points.
2. A branch `fix/<issue>-<words>` or `feature/<issue>-<words>` from `main`.
3. A pull request: CI must be green (ruff, Django checks, migrations, all tests on MySQL 8.0, coverage at least
   85%, Bandit, Docker build) and the review partner must approve.
4. The repository owner merges. A bug fix is released as a patch tag (`v1.0.1`, `v1.0.2`, ...); a new feature
   as a minor version (`v1.1`).
5. The RTM row, the STP test case table and `docs/DEVIATIONS.md` are updated in the same pull request when the
   behaviour or a requirement changes.

A fix for a bug always comes with a test that failed before the fix.

## The four kinds of maintenance

| Kind | What it covers in SAMS | Examples planned now |
|---|---|---|
| Corrective | Bugs found in use | Triage within 2 working days; security bugs (access, ownership, lockout, audit) fixed first |
| Adaptive | Keeping up with the platform | Move from MySQL 8.0 (end of support April 2026) to MySQL 8.4 LTS; follow Django 5.2 LTS patch releases; keep Python at a supported 3.x |
| Perfective | Improvements users ask for | Email or SMS alerts for low attendance; import students from a spreadsheet; more report filters |
| Preventive | Lowering future risk | Tests for the branches no test takes yet ([branch coverage report](reports/coverage/branch-coverage-report.md)); turn on HSTS once a trusted certificate is used; SonarCloud grade with the `SONAR_TOKEN` secret |

## Routine tasks

| Task | How often | How | Owner |
|---|---|---|---|
| Database backup | Nightly | Host cron: `docker compose exec -T web python manage.py backup_db --keep 14` (`DEVELOPING.md`) | Anmol |
| Restore drill | Monthly | Restore the latest backup into a scratch database and log in (as TC-Recovery-01 does) | Anmol |
| Read the audit log | Weekly | Look for repeated FAILED logins and DENIED pages | Anusha |
| Dependency updates | Monthly | `pip list --outdated`; one pull request per update, CI must pass | Anupriya |
| Security scan | Every pull request | Bandit in CI; also `pip-audit` before each release | Anupriya |
| TLS certificate | Before expiry (`TLS_DAYS`, 365 days by default) | Replace the files in `/etc/nginx/certs/` and restart Nginx | Anmol |
| Full test and system validation run | Before every release tag | `pytest` with coverage, then `tools/system_validation.py` against a fresh database | Anusha, Anupriya |

## Known limitations carried into maintenance

| Limitation | Why it is acceptable now | Planned action |
|---|---|---|
| HSTS is off | The local certificate is self-signed; HSTS with it would lock browsers out | `DJANGO_HSTS_SECONDS=31536000` once a trusted certificate is installed |
| Load tested to 20 users at once | The SRS target (SAM-NF-007) for one department | Re-test with more workers before a college-wide rollout |
| Cross-browser checks beyond Chrome were spot checks | STP Section 4 | Run the UX checks in Firefox and Edge before rollout |
| Backups are Django JSON, not `mysqldump` | Works on MySQL and SQLite, so the recovery test runs in CI | Switch to `mysqldump` if the database grows past a few hundred MB |

## Ending support

When SAMS is retired, the last backup and the audit log are kept for the period the college requires, then
deleted. The repository stays archived with the final tag.
