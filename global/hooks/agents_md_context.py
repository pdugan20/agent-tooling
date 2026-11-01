#!/usr/bin/env python3
"""SessionStart hook that gives Claude the repository's AGENTS.md instructions.

Claude Code 2.1.277 and later reads a repository's AGENTS.md natively when no
CLAUDE.md, .claude/CLAUDE.md, or CLAUDE.local.md exists in the working directory
or any directory above it. Older versions, and sessions where such a file exists,
do not read AGENTS.md at all. Codex, Cursor, and other agents read AGENTS.md, so
a repository that keeps AGENTS.md as its only instruction file would be
invisible to those Claude sessions unless it added a CLAUDE.md shim. This hook
removes the need for that shim, including hidden, git-excluded ones, and stays
silent when Claude already loads AGENTS.md natively so the file is not injected
twice.

For each directory from the repository root down to the session's working
directory, the hook returns AGENTS.md when Claude would not already load it.
Claude already loads it when that directory has a CLAUDE.md or .claude/CLAUDE.md
(the repository's own choice), or a CLAUDE.local.md that imports AGENTS.md.
Files are returned root first, the same order Claude uses for CLAUDE.md.

Nested AGENTS.md files below the working directory are left to Claude. When
native loading applies, Claude reads a subdirectory's AGENTS.md as it opens files
there, unless that subdirectory has its own CLAUDE.md. When this hook supplies
the chain instead, nothing loads those nested files; no hook event fires as
Claude moves into a subdirectory.

The hook never fails a session. Unreadable input, a missing file, or any other
error produces no output and exit 0.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_BYTES_PER_FILE = 64_000


def repository_root(start: Path) -> Path | None:
    for directory in (start, *start.parents):
        if (directory / ".git").exists():
            return directory
    return None


def directory_chain(cwd: Path) -> list[Path]:
    root = repository_root(cwd)
    if root is None:
        return [cwd]
    chain = [cwd]
    while chain[-1] != root:
        chain.append(chain[-1].parent)
    return list(reversed(chain))


def claude_already_loads_agents(directory: Path) -> bool:
    if (directory / "CLAUDE.md").exists() or (directory / ".claude" / "CLAUDE.md").exists():
        return True
    local = directory / "CLAUDE.local.md"
    if local.is_file():
        try:
            return "@AGENTS.md" in local.read_text(errors="replace")
        except OSError:
            return False
    return False


NATIVE_AGENTS_VERSION = (2, 1, 277)


def claude_version() -> tuple[int, ...] | None:
    override = os.environ.get("AGENTS_MD_HOOK_CLAUDE_VERSION")
    try:
        output = (
            override
            or subprocess.run(
                ["claude", "--version"], capture_output=True, text=True, timeout=3, check=False
            ).stdout
        )
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", output or "")
    return tuple(int(part) for part in match.groups()) if match else None


def project_claude_file_exists(chain: list[Path]) -> bool:
    return any(
        (directory / "CLAUDE.md").exists()
        or (directory / ".claude" / "CLAUDE.md").exists()
        or (directory / "CLAUDE.local.md").exists()
        for directory in chain
    )


def claude_reads_agents_natively(chain: list[Path]) -> bool:
    """True when this Claude session loads AGENTS.md on its own.

    Claude reads AGENTS.md only when no project CLAUDE.md, .claude/CLAUDE.md, or
    CLAUDE.local.md exists in the working directory or above it; ~/.claude/CLAUDE.md
    does not count. An unknown version is treated as not native so the hook keeps
    its older behavior rather than silently dropping instructions.
    """
    version = claude_version()
    if version is None or version < NATIVE_AGENTS_VERSION:
        return False
    return not project_claude_file_exists(chain)


def render(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    text = raw[:MAX_BYTES_PER_FILE].decode("utf-8", errors="replace").strip()
    if not text:
        return None
    note = ""
    if len(raw) > MAX_BYTES_PER_FILE:
        note = f"\n\n[Truncated at {MAX_BYTES_PER_FILE} bytes. Read {path} for the rest.]"
    header = (
        f"Repository instructions from {path}. This Claude Code session does not "
        "load AGENTS.md natively (a project CLAUDE.md exists above the working "
        "directory, or the version predates 2.1.277), so a SessionStart hook "
        "supplied this file. Follow it as you would a CLAUDE.md in the same directory."
    )
    return f"{header}\n\n{text}{note}"


def build_context(cwd: Path) -> str:
    chain = directory_chain(cwd)
    if claude_reads_agents_natively(chain):
        return ""
    sections = []
    for directory in chain:
        agents = directory / "AGENTS.md"
        if not agents.is_file() or claude_already_loads_agents(directory):
            continue
        rendered = render(agents)
        if rendered:
            sections.append(rendered)
    return "\n\n---\n\n".join(sections)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        raw_cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        context = build_context(Path(raw_cwd).resolve())
    except Exception:
        return 0
    if context:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
