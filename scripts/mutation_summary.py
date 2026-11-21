"""Turn mutmut CI stats JSON into a kill-rate summary (T-131).

Implements: T-131, NFR-MNT-001
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def kill_rate_from_stats(stats: dict[str, int]) -> tuple[int, int, float]:
    """Return ``(killed, survived, percent)``.

    Timeouts count as killed, matching mutmut's CI badge. Skipped mutants are
    excluded from the denominator.
    """
    killed = int(stats.get("killed", 0))
    survived = int(stats.get("survived", 0))
    timeout = int(stats.get("timeout", 0))
    caught = killed + timeout
    total = caught + survived
    percent = (100.0 * caught / total) if total else 0.0
    return caught, survived, percent


def summary_markdown(stats: dict[str, int]) -> str:
    """Markdown kill-rate block for the Actions job summary."""
    caught, survived, percent = kill_rate_from_stats(stats)
    return (
        "## Mutation testing\n\n"
        f"- killed (including timeouts): {caught}\n"
        f"- survived: {survived}\n"
        f"- kill rate: {percent:.1f}%\n"
    )


def summary_html(stats: dict[str, int]) -> str:
    """Standalone HTML report."""
    body = summary_markdown(stats).replace("\n", "<br>\n")
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>mutmut</title></head>"
        f"<body>{body}</body></html>\n"
    )


def main() -> None:
    """Print a markdown summary, optionally writing HTML."""
    parser = argparse.ArgumentParser()
    parser.add_argument("stats", type=Path)
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args()
    payload = json.loads(args.stats.read_text(encoding="utf-8")) if args.stats.exists() else {}
    if not isinstance(payload, dict):
        payload = {}
    print(summary_markdown(payload), end="")
    if args.html is not None:
        args.html.write_text(summary_html(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
