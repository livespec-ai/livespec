"""Contract test for the doctor's open spec-PR discovery query."""

from __future__ import annotations

from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
_OBJECTIVE_CHECKS_PROMPT = (
    _REPO_ROOT
    / ".claude-plugin"
    / "specification-templates"
    / "livespec"
    / "prompts"
    / "doctor-llm-objective-checks.md"
)


def test_open_spec_pr_query_filters_open_prs_by_head_ref_prefix() -> None:
    """Discovery filters all open PRs on `headRefName`, not a `--head` glob."""
    prompt = _OBJECTIVE_CHECKS_PROMPT.read_text(encoding="utf-8")

    assert "--head" not in prompt
    assert 'startswith("spec/")' in prompt
