"""TC-Maint-01 (SAM-NF-006): the code stays easy to change.

Owner: Anmol Vyas. Checks what a reviewer would otherwise check by hand:
- the lint check passes and no function is too complex (cyclomatic complexity 10 or less);
- the quality gates are wired into CI (tests with an 85% coverage floor, lint, Bandit);
- every module that has views also has tests that open its pages.
The module boundaries themselves are covered by tests/test_architecture.py.
"""
import importlib.util
import re
import subprocess  # nosec B404 - runs ruff, a fixed local command
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

needs_ruff = pytest.mark.skipif(
    importlib.util.find_spec("ruff") is None, reason="ruff isn't installed here (CI has it)"
)


def ruff(*args):
    return subprocess.run(  # nosec B603 - fixed arguments, no shell
        [sys.executable, "-m", "ruff", *args], cwd=ROOT, capture_output=True, text=True
    )


@needs_ruff
def test_tc_maint_01a_lint_passes():
    result = ruff("check", ".")
    assert result.returncode == 0, result.stdout


@needs_ruff
def test_tc_maint_01b_no_function_is_too_complex():
    result = ruff("check", ".", "--select", "C901", "--config", "lint.mccabe.max-complexity = 10")
    assert result.returncode == 0, result.stdout


def test_tc_maint_01c_quality_gates_run_in_ci():
    assert re.search(r"coverage report --fail-under=(\d+)", CI) and int(
        re.search(r"--fail-under=(\d+)", CI).group(1)
    ) >= 85
    assert "ruff check ." in CI
    assert "bandit -r ." in CI
    assert "makemigrations --check" in CI


@pytest.mark.parametrize(
    "module,url_part",
    [
        ("students", "/students/"), ("faculty", "/faculty/"), ("subjects", "/subjects/"),
        ("attendance", "/attendance/"), ("calculation", "/percentage/"), ("notification", "/notifications/"),
        ("reports", "/reports/"), ("audit", "/audit/"), ("dashboards", "/dashboard/"),
    ],
)
def test_tc_maint_01d_every_module_with_pages_has_tests_for_them(module, url_part):
    tests = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "tests").glob("test_*.py"))
    assert url_part in tests, f"no test opens a {module} page ({url_part})"
