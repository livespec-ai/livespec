"""Acceptance coverage for the public-API Result-railway adoption.

The un-gated public-api-result-typed checker correctly treats the three
``dev-tooling`` ``main()`` functions below as public.  They are outermost
supervisors, however, so the repository must declare their files in the
per-file supervisor role instead of putting their process boundaries on the
Result railway.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__: list[str] = []


_REPO_ROOT = Path(__file__).resolve().parents[1]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"
_OUTERMOST_SUPERVISOR_FILES = {
    "dev-tooling/gh_feature_surfaces.py",
    "dev-tooling/reap_stale_worktrees.py",
    "dev-tooling/refresh_tenant_repos.py",
}


def _supervisor_entry_files() -> set[str]:
    text = _PYPROJECT.read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^supervisor_entry_files\s*=\s*\[(?P<entries>.*?)^\]",
        text,
    )
    assert match is not None, "pyproject.toml must declare supervisor_entry_files"
    return set(re.findall(r'"([^"\n]+)"', match.group("entries")))


def test_un_gated_railway_cli_supervisors_are_declared() -> None:
    declared = _supervisor_entry_files()
    assert _OUTERMOST_SUPERVISOR_FILES <= declared, (
        "the un-gated public-API Result checker reaches these outermost CLI "
        f"supervisors, but they are absent from supervisor_entry_files: "
        f"{sorted(_OUTERMOST_SUPERVISOR_FILES - declared)}"
    )
