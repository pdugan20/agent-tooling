#!/usr/bin/env python3

"""Compare the configured Superpowers baseline with upstream main."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config/superpowers.json"


def resolve_remote_commit(repository: str) -> str:
    completed = subprocess.run(
        ["git", "ls-remote", repository, "refs/heads/main"],
        check=True,
        capture_output=True,
        text=True,
    )
    fields = completed.stdout.strip().split()
    if len(fields) != 2 or fields[1] != "refs/heads/main" or len(fields[0]) != 40:
        raise ValueError(f"Unexpected git ls-remote output for {repository}")
    return fields[0]


def build_status(configuration: dict[str, Any]) -> dict[str, Any]:
    current = str(configuration["upstreamCommit"])
    latest = resolve_remote_commit(str(configuration["upstreamRepository"]))
    return {
        "currentCommit": current,
        "forkVersion": configuration["forkVersion"],
        "latestCommit": latest,
        "outdated": current != latest,
        "upstreamRepository": configuration["upstreamRepository"],
        "upstreamVersion": configuration["upstreamVersion"],
    }


def write_github_output(status: dict[str, Any], path: Path) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key in ("currentCommit", "latestCommit", "outdated", "upstreamVersion", "forkVersion"):
            value = status[key]
            if isinstance(value, bool):
                value = str(value).lower()
            handle.write(f"{key}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when upstream main differs from the recorded baseline.",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Append status fields to the path in GITHUB_OUTPUT.",
    )
    args = parser.parse_args()

    configuration = json.loads(CONFIG.read_text(encoding="utf-8"))
    status = build_status(configuration)
    print(json.dumps(status, indent=2, sort_keys=True))

    if args.github_output:
        output = os.environ.get("GITHUB_OUTPUT")
        if not output:
            raise SystemExit("GITHUB_OUTPUT is required with --github-output")
        write_github_output(status, Path(output))

    if args.check and status["outdated"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
