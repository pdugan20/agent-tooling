#!/usr/bin/env python3

"""Report machine-local Codex MCP authentication health."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "config/codex-mcp-auth.json"
AUTHENTICATED_STATUSES = {"logged_in", "o_auth", "oauth"}


@dataclass(frozen=True)
class Check:
    label: str
    name: str
    detail: str = ""
    failure: bool = False


def load_servers() -> list[dict[str, Any]]:
    try:
        completed = subprocess.run(
            ["codex", "mcp", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("Codex CLI is not installed or is not on PATH.") from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip() or "unknown error"
        raise RuntimeError(f"Unable to list Codex MCP servers: {message}") from error

    try:
        servers = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Codex returned invalid JSON for the MCP server list.") from error
    if not isinstance(servers, list):
        raise RuntimeError("Codex returned an unexpected MCP server list shape.")
    return servers


def evaluate(
    servers: list[dict[str, Any]], policy: dict[str, Any]
) -> tuple[list[Check], list[Check]]:
    by_name = {
        str(server.get("name")): server
        for server in servers
        if isinstance(server, dict) and server.get("name")
    }
    expected_names: set[str] = set()
    checks: list[Check] = []

    for name in policy["oauthRequired"]:
        expected_names.add(name)
        server = by_name.get(name)
        if server is None:
            checks.append(Check("MISSING", name, "Expected protected MCP is not installed.", True))
        elif server.get("auth_status") in AUTHENTICATED_STATUSES:
            checks.append(Check("CONNECTED", name))
        else:
            checks.append(
                Check(
                    "NEEDS LOGIN",
                    name,
                    f"Run: codex mcp login {json.dumps(name)}",
                    True,
                )
            )

    for name, blocker in policy["knownBlocked"].items():
        expected_names.add(name)
        server = by_name.get(name)
        if server is None:
            checks.append(Check("MISSING", name, "Expected MCP is not installed.", True))
        elif server.get("auth_status") in AUTHENTICATED_STATUSES:
            checks.append(Check("CONNECTED", name))
        else:
            checks.append(Check("BLOCKED", name, f"{blocker['reason']} {blocker['issue']}"))

    for name, reason in policy["noOAuthRequired"].items():
        expected_names.add(name)
        if name in by_name:
            checks.append(Check("NO OAUTH", name, reason))
        else:
            checks.append(Check("MISSING", name, "Expected MCP is not installed.", True))

    additional: list[Check] = []
    for name in sorted(by_name.keys() - expected_names, key=str.casefold):
        status = str(by_name[name].get("auth_status", "unknown"))
        if status in AUTHENTICATED_STATUSES:
            label = "CONNECTED"
        elif status == "not_logged_in":
            label = "NEEDS REVIEW"
        elif status == "unsupported":
            label = "NO OAUTH"
        else:
            label = status.upper().replace("_", " ")
        additional.append(Check(label, name, f"Codex status: {status}."))

    return checks, additional


def format_check(check: Check) -> str:
    line = f"{check.label:<12} {check.name}"
    if check.detail:
        line += f" — {check.detail}"
    return line


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Read a saved `codex mcp list --json` payload instead of invoking Codex.",
    )
    args = parser.parse_args()

    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    servers = json.loads(args.input.read_text(encoding="utf-8")) if args.input else load_servers()

    checks, additional = evaluate(servers, policy)
    for check in checks:
        print(format_check(check))
    if additional:
        print("\nAdditional runtime-managed MCP servers:")
        for check in additional:
            print(format_check(check))

    failures = sum(check.failure for check in checks)
    connected = sum(check.label == "CONNECTED" for check in checks)
    blocked = sum(check.label == "BLOCKED" for check in checks)
    print(f"\nSummary: {connected} connected, {blocked} blocked, {failures} action required.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
