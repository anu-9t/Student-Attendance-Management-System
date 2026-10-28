# Developing SAMS

## Run everything with Docker (same for every member)
```
cp .env.example .env        # then edit the passwords
docker compose up --build
docker compose exec web python manage.py createsuperuser   # or use seed_data
docker compose exec web python manage.py seed_data
```
Open https://localhost/ (the development certificate is self-signed; accept it in the browser).
The health check is https://localhost/health/ and the admin site is https://localhost/admin/.
HTTP requests on port 80 redirect to HTTPS. For a real deployment, mount trusted TLS files
at `/etc/nginx/certs/server.crt` and `/etc/nginx/certs/server.key` in the Nginx container.

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

## Backup and restore (SAM-NF-005)
```
docker compose exec web python manage.py backup_db --keep 14     # writes backups/sams-<date>.json.gz
docker compose exec web python manage.py restore_db backups/sams-20261028-110000.json.gz
```
Backups land in the `backups/` folder next to docker-compose.yml (it's in .gitignore). A restore
replaces everything in the database, so it asks you to type `restore` first (or pass `--yes`).
Both write an entry to the audit log. The files are plain JSON, so a backup taken from MySQL
restores into SQLite and back. To back up every night, add a cron job on the host, e.g.
`0 2 * * * cd /path/to/sams && docker compose exec -T web python manage.py backup_db --keep 14`.

## Where things go
One Django app per module (SAD 3.5): accounts, students, faculty, subjects, attendance, calculation,
notification, reports, audit. Each module adds its own `urls.py`, templates and tests, and includes its
URLs in `sams/urls.py`. Work on a branch, open a pull request, and get a review from someone who did not write it.
