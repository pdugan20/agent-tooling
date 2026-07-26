#!/usr/bin/env python3

"""Apply portable, non-secret Codex configuration fixes."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

import tomllib

FALLBACK_LINE = 'project_doc_fallback_filenames = ["CLAUDE.md"]'
FALLBACK_RE = re.compile(r"^project_doc_fallback_filenames\s*=.*$", re.MULTILINE)
COMPUTER_USE_SECTION = "[mcp_servers.computer-use]"
RELATIVE_COMPUTER_USE_COMMAND = (
    "./Codex Computer Use.app/Contents/SharedSupport/"
    "SkyComputerUseClient.app/Contents/MacOS/SkyComputerUseClient"
)
COMPUTER_USE_SUFFIX = (
    ".codex/computer-use/Codex Computer Use.app/Contents/SharedSupport/"
    "SkyComputerUseClient.app/Contents/MacOS/SkyComputerUseClient"
)


def _insert_root_fallback(text: str) -> str:
    """Ensure the fallback key is top-level rather than inside a TOML table."""

    try:
        parsed = tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Refusing to modify invalid TOML: {error}") from error

    if parsed.get("project_doc_fallback_filenames") == ["CLAUDE.md"]:
        return text

    lines = [line for line in text.splitlines() if not FALLBACK_RE.fullmatch(line)]
    table_index = next(
        (index for index, line in enumerate(lines) if line.lstrip().startswith("[")),
        len(lines),
    )
    lines[table_index:table_index] = [FALLBACK_LINE, ""]

    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return f"{normalized}\n" if normalized else f"{FALLBACK_LINE}\n"


def _repair_computer_use_command(text: str, home: Path) -> str:
    client = home / COMPUTER_USE_SUFFIX
    if not os.access(client, os.X_OK):
        return text

    lines = text.splitlines()
    in_computer_use = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            in_computer_use = stripped == COMPUTER_USE_SECTION
            continue
        if not in_computer_use or not stripped.startswith("command"):
            continue

        match = re.fullmatch(r'command\s*=\s*"([^"]*)"\s*', stripped)
        if match and match.group(1) == RELATIVE_COMPUTER_USE_COMMAND:
            lines[index] = f"command = {json.dumps(str(client))}"
        break

    return "\n".join(lines) + "\n"


def update_config(text: str, home: Path) -> str:
    """Return an updated config without changing secrets or runtime auth."""

    return _repair_computer_use_command(_insert_root_fallback(text), home)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()

    args.config.parent.mkdir(parents=True, exist_ok=True)
    original = args.config.read_text() if args.config.exists() else ""
    updated = update_config(original, args.home)
    if updated == original:
        return

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=args.config.parent,
        prefix=f".{args.config.name}.",
        delete=False,
    ) as handle:
        handle.write(updated)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, args.config)


if __name__ == "__main__":
    main()
