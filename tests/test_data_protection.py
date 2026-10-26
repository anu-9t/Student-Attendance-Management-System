"""SAM-NF-004 (data protection): secure cookies, HTTPS-only settings and safe headers."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.django_db


def production_settings(**env):
    """Load the settings the way the container does (DJANGO_DEBUG=0) and read a few values."""
    names = ["SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE", "SECURE_SSL_REDIRECT", "SECURE_HSTS_SECONDS"]
    code = (
        "import json, sams.settings as s; "
        f"print(json.dumps({{n: getattr(s, n, None) for n in {names!r}}}))"
    )
    run_env = {**os.environ, "DJANGO_DEBUG": "0", **env}
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=run_env, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_cookies_are_https_only_in_production():
    values = production_settings()
    assert values["SESSION_COOKIE_SECURE"] is True
    assert values["CSRF_COOKIE_SECURE"] is True
    assert values["SECURE_SSL_REDIRECT"] is True


def test_hsts_is_off_until_turned_on():
    assert production_settings()["SECURE_HSTS_SECONDS"] == 0
    assert production_settings(DJANGO_HSTS_SECONDS="31536000")["SECURE_HSTS_SECONDS"] == 31536000


def test_session_cookie_is_hidden_from_scripts_and_expires():
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_AGE == 30 * 60
    assert settings.SESSION_EXPIRE_AT_BROWSER_CLOSE is True


def test_pages_send_safe_headers(client):
    response = client.get("/login/")
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "same-origin"


def test_nginx_sends_the_same_headers():
    conf = (ROOT / "nginx" / "nginx.conf").read_text()
    for header in ["X-Content-Type-Options nosniff", "X-Frame-Options DENY", "Referrer-Policy same-origin"]:
        assert header in conf
    assert "return 301 https://" in conf
