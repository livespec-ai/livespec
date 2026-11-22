"""The bare ``pytest --cov=<pkg>`` spelling combines its coverage data.

Work-item livespec-uy7ur2. A full suite run with the bare spelling can pass
every test, then fail while pytest-cov combines statement-only subprocess
data with branch data. The repository's coverage configuration enables branch
coverage in ``pyproject.toml``; pytest-cov only passes that config to child
processes when ``--cov-config`` names it.

This test builds a throwaway project from this repository's real pytest
configuration and runs the bare spelling. Its subprocess deliberately runs
outside that project's root, which reproduces the config-discovery boundary
that previously produced incompatible coverage data.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PACKAGE = "def f(x):\n    if x:\n        return 1\n    return 2\n"
_SUITE = """\
import subprocess
import sys


def test_subprocess_without_a_pyproject_in_view(tmp_path):
    code = "import pkg; pkg.f(1)"
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)


def test_main_process_measures_the_same_package():
    import pkg

    assert pkg.f(0) == 2
"""


def _pytest_section() -> str:
    text = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^\[tool\.pytest\.ini_options\]\n.*?(?=^\[)", text, re.DOTALL | re.MULTILINE)
    assert match is not None
    return match.group(0)


def _clean_env(*, project: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("COV_CORE_", "COVERAGE_", "LIVESPEC_COVERAGE_"))
        and key not in {"PYTEST_ADDOPTS", "PYTEST_CURRENT_TEST"}
    }
    env["PYTHONPATH"] = str(project)
    return env


def test_bare_cov_spelling_combines_branch_and_subprocess_data(*, tmp_path: Path) -> None:
    """A full run with the bare spelling ends green and prints a coverage report."""
    project = tmp_path / "project"
    (project / "pkg").mkdir(parents=True)
    (project / "tests").mkdir()
    _ = (project / "pkg" / "__init__.py").write_text(_PACKAGE, encoding="utf-8")
    _ = (project / "tests" / "test_demo.py").write_text(_SUITE, encoding="utf-8")
    _ = (project / "pyproject.toml").write_text(
        f"[tool.coverage.run]\nbranch = true\n\n{_pytest_section()}", encoding="utf-8"
    )
    command = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--cov=pkg"]
    completed = subprocess.run(
        command,
        cwd=project,
        env=_clean_env(project=project),
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    assert "Can't combine" not in output, output
    assert completed.returncode == 0, output
    assert "TOTAL" in output, output
