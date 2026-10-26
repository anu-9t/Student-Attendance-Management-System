FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_HTTP_TIMEOUT=60 \
    UV_HTTP_RETRIES=5
WORKDIR /app

# uv is a fast, drop-in replacement for pip's requirements-file workflow.
# Pin the image tag so dependency installation does not change unexpectedly.
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

# mysqlclient needs the MySQL client headers; mysqldump is used by backup_db
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential default-libmysqlclient-dev pkg-config default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# mysqlclient may be built from source on Linux; the apt packages above provide
# its compiler and MySQL client headers. uv handles the Python dependencies.
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
CMD ["gunicorn", "sams.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
