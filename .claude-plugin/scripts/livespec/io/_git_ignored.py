"""Git-ignore queries for paths in a project's working tree."""

from __future__ import annotations

from pathlib import Path

from returns.io import IOResult

from livespec.errors import LivespecError
from livespec.io.proc import run_subprocess

__all__: list[str] = ["list_ignored_paths"]


def list_ignored_paths(
    *,
    project_root: Path,
    paths: list[Path],
) -> IOResult[frozenset[Path], LivespecError]:
    """Return paths excluded by the project's Git ignore rules.

    ``git check-ignore`` uses the repository's effective ignore rules,
    including nested ignore files and global configuration. ``--no-index``
    asks about the rules even when a path is tracked. A non-repository or a
    no-match response writes no stdout, which correctly yields an empty set.
    """
    relative_paths = [path.relative_to(project_root) for path in paths]
    input_text = "\0".join(str(path) for path in relative_paths)
    if input_text:
        input_text += "\0"
    return run_subprocess(
        argv=[
            "git",
            "-C",
            str(project_root),
            "check-ignore",
            "--no-index",
            "--stdin",
            "-z",
        ],
        input_text=input_text,
    ).map(
        lambda completed: frozenset(
            project_root / raw_path for raw_path in completed.stdout.split("\0") if raw_path
        ),
    )
