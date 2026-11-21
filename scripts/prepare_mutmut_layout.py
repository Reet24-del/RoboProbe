"""Copy repo data to ``backend/`` so mutmut's copied tests can open it.

mutmut runs pytest with cwd ``backend/mutants``. ``Path(__file__).parents[N]`` in
those copies lands on ``backend/`` rather than the repository root.

Implements: T-131, NFR-MNT-001
"""

from __future__ import annotations

import shutil
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_BACKEND = _REPO / "backend"
_DIRS = ("configs", "schemas", "tasks", "scripts", "docs")
_FILES = ("roboprobe.example.toml", ".env.example")


def main() -> None:
    """Replace the backend copies of the directories and files tests open."""
    for name in _DIRS:
        destination = _BACKEND / name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(_REPO / name, destination, symlinks=True)
    for name in _FILES:
        shutil.copy2(_REPO / name, _BACKEND / name)


if __name__ == "__main__":
    main()
