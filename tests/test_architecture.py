"""SAM-NF-006 (maintainability): the module structure from SAD 3.5 stays as designed.

These tests fail when a change quietly breaks a boundary, so it gets talked about in review.
"""
import ast
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings
from django.urls import get_resolver

ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    "accounts", "students", "faculty", "subjects", "attendance",
    "calculation", "notification", "reports", "audit", "dashboards",
]


def python_files(module):
    return [p for p in (ROOT / module).rglob("*.py") if "migrations" not in p.parts]


def imports_of(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name


@pytest.mark.parametrize("module", MODULES)
def test_every_module_is_an_installed_app(module):
    assert module in settings.INSTALLED_APPS
    assert apps.is_installed(module)


@pytest.mark.parametrize("module", MODULES)
def test_every_module_has_its_own_urls_and_namespace(module):
    urls = ROOT / module / "urls.py"
    assert urls.exists(), f"{module}/urls.py is missing"
    assert "app_name =" in urls.read_text(encoding="utf-8")


def test_every_module_is_reachable_from_the_root_urls():
    namespaces = set(get_resolver().namespace_dict)
    missing = [m for m in MODULES if m not in namespaces and m != "accounts"]
    assert not missing, f"not included in sams/urls.py: {missing}"


@pytest.mark.parametrize("module", MODULES)
def test_no_module_imports_another_modules_views(module):
    offenders = []
    for path in python_files(module):
        for name in imports_of(path):
            parts = name.split(".")
            if len(parts) >= 2 and parts[0] in MODULES and parts[0] != module and parts[1] == "views":
                offenders.append(f"{path.relative_to(ROOT)} imports {name}")
    assert not offenders, "use a service function instead of another module's views: " + "; ".join(offenders)


def test_only_the_audit_module_writes_audit_entries():
    offenders = []
    for module in MODULES:
        if module == "audit":
            continue
        for path in python_files(module):
            text = path.read_text(encoding="utf-8")
            if "AuditLog.objects.create" in text or "AuditLog(" in text:
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"write audit entries through audit.services.record(): {offenders}"


def test_templates_are_grouped_by_module():
    loose = [p.name for p in (ROOT / "templates").glob("*.html") if p.name not in {"base.html", "403.html", "404.html", "500.html"}]
    assert not loose, f"put page templates in templates/<module>/: {loose}"
