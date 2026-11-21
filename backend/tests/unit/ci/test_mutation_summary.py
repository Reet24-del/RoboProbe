"""Kill-rate summary for the weekly mutmut workflow (T-131)."""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _repo() -> Path:
    """Repo root in a normal checkout and under mutmut's copied tests tree."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "backend" / "pyproject.toml"
        if candidate.is_file():
            return parent
    msg = "repo root not found"
    raise AssertionError(msg)


_REPO = _repo()


def _summary():
    path = _REPO / "scripts/mutation_summary.py"
    spec = importlib.util.spec_from_file_location("mutation_summary", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kill_rate_counts_timeouts_as_killed() -> None:
    summary = _summary()
    caught, survived, percent = summary.kill_rate_from_stats(
        {"killed": 7, "survived": 2, "timeout": 1}
    )
    assert (caught, survived, percent) == (8, 2, 80.0)


def test_mutmut_config_targets_selection_and_oracles() -> None:
    pyproject = tomllib.loads((_REPO / "backend/pyproject.toml").read_text(encoding="utf-8"))
    tool = pyproject["tool"]["mutmut"]
    assert tool["source_paths"] == ["src"]
    assert "src/roboprobe/selection/*.py" in tool["only_mutate"]
    assert "src/roboprobe/oracles/*.py" in tool["only_mutate"]
    args = tool["pytest_add_cli_args"]
    assert args[:4] == ["-x", "-q", "-m", "unit or property"]
    assert "not test_every_logged_event_is_in_the_catalogue" in args
