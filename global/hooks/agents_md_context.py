#!/usr/bin/env python3
"""SessionStart hook that gives Claude the repository's AGENTS.md instructions.

Claude Code loads CLAUDE.md files but not AGENTS.md. Codex, Cursor, and other
agents read AGENTS.md, so a repository that keeps AGENTS.md as its only
instruction file is invisible to Claude unless it adds a CLAUDE.md shim. This
hook removes the need for that shim, including hidden, git-excluded ones.

For each directory from the repository root down to the session's working
directory, the hook returns AGENTS.md when Claude would not already load it.
Claude already loads it when that directory has a CLAUDE.md or .claude/CLAUDE.md
(the repository's own choice), or a CLAUDE.local.md that imports AGENTS.md.
Files are returned root first, the same order Claude uses for CLAUDE.md.

Nested AGENTS.md files below the working directory are not loaded. Claude loads
nested CLAUDE.md files lazily, and no hook event does that for AGENTS.md.

The hook never fails a session. Unreadable input, a missing file, or any other
error produces no output and exit 0.
"""

from __future__ import annotations

import json
import os
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
        f"Repository instructions from {path}. Claude Code does not load AGENTS.md "
        "by itself, so a SessionStart hook supplied this file. Follow it as you "
        "would a CLAUDE.md in the same directory."
    )
    return f"{header}\n\n{text}{note}"


def build_context(cwd: Path) -> str:
    sections = []
    for directory in directory_chain(cwd):
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
