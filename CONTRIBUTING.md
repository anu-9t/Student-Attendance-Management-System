# Working on SAMS

## Branches and pull requests

- One branch per issue: `feature/<issue number>-<two or three words>`, for example `feature/9-add-student`.
- Every change reaches `main` through a pull request. Nobody pushes to `main` directly or presses
  Merge on their own pull request; Anupam (repo owner) merges.
- Each pull request is reviewed by a member who did not write it (SAD 4.1.2, Table 3):
  Anupam reviews Anmol, Anmol reviews Anupam, Anusha reviews Anupriya, Anupriya reviews Anusha.

## Quality gates (checked by CI on every pull request)

- All tests pass (`pytest`), and line coverage stays at 85% or more.
- `python manage.py check` passes and every model change has a migration.
- Bandit finds no medium or high severity issues.
- The Docker image builds.

A pull request is merged only when CI is green and a reviewer has approved it.

## Commit messages

Short and plain, saying what changed: "Add the attendance marking sheet", not "Update views.py".
Put `Closes #<issue>` on the last commit of the issue.

## Defects

Bugs found while testing go in as GitHub issues with the label `bug`, the steps to reproduce,
and what was expected. The QA lead triages them and assigns an owner.
