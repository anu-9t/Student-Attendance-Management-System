"""SAM-NF-002 (availability): every container restarts on its own and has a health check."""
import re
from pathlib import Path

import pytest

COMPOSE = (Path(__file__).resolve().parent.parent / "docker-compose.yml").read_text()


def service_block(name):
    match = re.search(rf"^  {name}:\n(.*?)(?=^  \S|^\S|\Z)", COMPOSE, re.S | re.M)
    assert match, f"service {name} missing from docker-compose.yml"
    return match.group(1)


@pytest.mark.parametrize("service", ["db", "web", "nginx"])
def test_every_container_restarts_itself(service):
    assert "restart: unless-stopped" in service_block(service)


@pytest.mark.parametrize("service", ["db", "web", "nginx"])
def test_every_container_has_a_health_check(service):
    assert "healthcheck:" in service_block(service)


def test_web_waits_for_the_database_and_nginx_waits_for_web():
    assert re.search(r"db:\s*\n\s*condition: service_healthy", service_block("web"))
    assert re.search(r"web:\s*\n\s*condition: service_healthy", service_block("nginx"))


@pytest.mark.django_db  # the health page now asks the database too
def test_web_health_check_uses_the_health_page(client):
    assert "/health/" in service_block("web")
    assert client.get("/health/").json() == {"status": "ok"}
