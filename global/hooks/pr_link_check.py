#!/usr/bin/env python3
"""Stop hook that holds every pull request mention to a link pair.

The global AGENTS.md says each pull request put in front of the user is a link
pair: the GitHub link and, for repositories that Linear review indexes, the
linear.review link. Agents keep it for the first mention and drop it for passing
ones, so this checks the finished reply.

Claude and Codex both send the Stop payload on stdin, and both carry the two
fields used here. `last_assistant_message` is the reply. `stop_hook_active` is
true when the turn already continued once because of a Stop hook, so this hook
blocks at most once per turn and cannot loop.

Exit 0 with no output lets the reply through. Exit 2 with the reason on stderr
sends the agent back to rewrite it. Codex rejects plain text on stdout for this
event, so nothing is ever printed there.

Which repositories Linear review indexes is private, so the list is read one
`owner/repo` per line from ~/.codex/local/linear-review-repos.txt. Without that
file only the bare-number check runs.

Fenced code and inline code are exempt, so a copy-paste block of URLs passes.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPOS_FILE = Path(
    os.environ.get("PR_LINK_REPOS_FILE", str(Path.home() / ".codex/local/linear-review-repos.txt"))
)

FENCED_RE = re.compile(r"(```|~~~).*?\1", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\([^)\s]+\)")
URL_RE = re.compile(r"https?://\S+")
# "#13081" in prose. Headings (##), HTML entities (&#123;) and URL fragments are excluded.
BARE_NUMBER_RE = re.compile(r"(?<![\w&/#])#(\d{2,6})\b")
GITHUB_PR_RE = re.compile(r"https?://github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)")
LINEAR_REVIEW_RE = re.compile(r"https?://linear\.review/([\w.-]+/[\w.-]+)/pull/(\d+)")


def strip_code(text: str) -> str:
    text = FENCED_RE.sub(" ", text)
    return INLINE_CODE_RE.sub(" ", text)


def load_repos(path: Path = REPOS_FILE) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {
        line.strip().lower() for line in lines if line.strip() and not line.lstrip().startswith("#")
    }


def find_problems(text: str, repos: set[str]) -> list[str]:
    body = strip_code(text)
    problems: list[str] = []

    prose = URL_RE.sub(" ", MARKDOWN_LINK_RE.sub(" ", body))
    bare = sorted({match.group(1) for match in BARE_NUMBER_RE.finditer(prose)}, key=int)
    if bare:
        problems.append("bare numbers with no link: " + ", ".join(f"#{number}" for number in bare))

    reviewed = {(repo.lower(), number) for repo, number in LINEAR_REVIEW_RE.findall(body)}
    missing = sorted(
        {
            f"{repo}#{number}"
            for repo, number in GITHUB_PR_RE.findall(body)
            if repo.lower() in repos and (repo.lower(), number) not in reviewed
        }
    )
    if missing:
        problems.append("GitHub link with no Linear review link: " + ", ".join(missing))
    return problems


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never fail a turn because the hook could not read its input
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return 0

    message = payload.get("last_assistant_message") or ""
    if not message.strip():
        return 0

    problems = find_problems(message, load_repos())
    if not problems:
        return 0

    lines = [
        "Your reply mentions pull requests without the link pair from AGENTS.md.",
        "Rewrite it so every pull request reads",
        "[#N](https://github.com/<owner>/<repo>/pull/N)"
        " · [Linear review](https://linear.review/<owner>/<repo>/pull/N),",
        "followed by its issue link when one exists. Keep everything else the same.",
    ]
    lines += [f"  - {problem}" for problem in problems]
    lines.append("Copy-paste lists can stay in a code block; code is not checked.")
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
