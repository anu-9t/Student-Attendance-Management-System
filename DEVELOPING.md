# Developing SAMS

## Run everything with Docker (same for every member)
```
cp .env.example .env        # then edit the passwords
docker compose up --build
docker compose exec web python manage.py createsuperuser   # or use seed_data
docker compose exec web python manage.py seed_data
```
Open http://localhost/ (health check: http://localhost/health/, admin: /admin/).

## Quick local run without Docker (SQLite, for fast tests only)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt     # mysqlclient needs the MySQL client headers; if it fails, install them or skip it for SQLite
DB_ENGINE=sqlite python manage.py migrate
DB_ENGINE=sqlite python manage.py seed_data
DB_ENGINE=sqlite python manage.py runserver
```

## Tests
```
DB_ENGINE=sqlite coverage run -m pytest && coverage report
```
CI runs the same tests against MySQL 8.0.

## Where things go
One Django app per module (SAD 3.5): accounts, students, faculty, subjects, attendance, calculation,
notification, reports, audit. Each module adds its own `urls.py`, templates and tests, and includes its
URLs in `sams/urls.py`. Work on a branch, open a pull request, and get a review from someone who did not write it.
