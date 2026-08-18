#!/usr/bin/env python3
"""Stop hook that holds Claude to the simple-english output style.

The style is configured globally in settings.json, but nothing checked it, so a
whole session could drift without either side noticing. This is the check.

Input arrives on stdin as the Stop hook payload. The field that matters is
`last_assistant_message`, which carries the finished reply, so the transcript
never has to be parsed.

Exit 0 lets the turn finish. Exit 2 blocks it and shows stderr to Claude, which
then rewrites the reply. To keep a stubborn phrasing from trapping the session,
each prompt is blocked at most once. The second attempt is allowed through.

Rules enforced here are the ones with exact string matches. Sentence length is
reported as advice only, because counting words around code spans and file paths
produces false positives, and a wrong block costs a whole regeneration.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

STATE_DIR = Path(os.environ.get("TMPDIR", "/tmp")) / "claude-simple-english"
STATE_TTL_SECONDS = 6 * 60 * 60

# Phrases that carry style but no fact. Add to this list whenever a habit annoys
# you. It is a plain substring match, so it stays cheap.
JARGON = [
    "load-bearing",
    "load bearing",
    "blast radius",
    "the tell is",
    "worth naming",
    "that is the whole",
    "tracer bullet",
    "first-class",
    "under the hood",
    "at the end of the day",
    "needle-moving",
    "delightful",
    "seamless",
    "robust",
    "powerful",
    "comprehensive",
    "leverage",
    "in order to",
    "it is worth noting",
    "simply put",
]

CONTRACTIONS = re.compile(
    r"\b(?:"
    r"can't|cannot've|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|"
    r"hasn't|haven't|hadn't|shouldn't|wouldn't|couldn't|mustn't|needn't|"
    r"I'm|I've|I'll|I'd|you're|you've|you'll|you'd|we're|we've|we'll|we'd|"
    r"they're|they've|they'll|they'd|it's|that's|there's|here's|what's|"
    r"let's|who's|he's|she's"
    r")\b",
    re.IGNORECASE,
)

MODALS = re.compile(r"\b(?:should|would)\b", re.IGNORECASE)


def strip_protected(text: str) -> str:
    """Remove spans the style explicitly protects, so they cannot trip a check.

    Code blocks, inline code, URLs, file paths and quoted error text are all
    exempt under the standard. Checking them produces noise, and a false block
    is more expensive than a missed one.
    """
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\b[\w.-]+/[\w./-]+", " ", text)  # file paths
    text = re.sub(r"^\s{4,}\S.*$", " ", text, flags=re.MULTILINE)  # indented code
    return text


def find_violations(text: str) -> list[str]:
    body = strip_protected(text)
    out: list[str] = []

    hits = sorted({m.group(0) for m in CONTRACTIONS.finditer(body)})
    if hits:
        out.append(f"contractions: {', '.join(hits[:6])}")

    if "—" in body:
        out.append("em dash: write two sentences, or use a comma")

    if ";" in body:
        out.append("semicolon: write two sentences")

    modal_hits = sorted({m.group(0).lower() for m in MODALS.finditer(body)})
    if modal_hits:
        out.append(f"banned modal: {', '.join(modal_hits)}. Write 'must' if required, or delete it")

    lowered = body.lower()
    jargon_hits = [j for j in JARGON if j in lowered]
    if jargon_hits:
        out.append(f"jargon with no fact: {', '.join(jargon_hits[:6])}")

    return out


def long_sentences(text: str, limit: int = 25) -> list[str]:
    body = strip_protected(text)
    body = re.sub(r"^\s*[-*|#>].*$", " ", body, flags=re.MULTILINE)  # lists, tables
    found = []
    for raw in re.split(r"(?<=[.!?])\s+", body):
        words = [w for w in raw.split() if w.strip()]
        if len(words) > limit:
            found.append(f"{len(words)} words: {' '.join(words[:9])}...")
    return found


def already_blocked(prompt_id: str) -> bool:
    """One block per prompt. The retry is allowed through either way."""
    if not prompt_id:
        return False
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for stale in STATE_DIR.glob("*"):
        try:
            if now - stale.stat().st_mtime > STATE_TTL_SECONDS:
                stale.unlink()
        except OSError:
            pass
    marker = STATE_DIR / re.sub(r"[^A-Za-z0-9_-]", "", prompt_id)[:64]
    if marker.exists():
        return True
    marker.touch()
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never fail a turn because the hook could not read its input

    message = payload.get("last_assistant_message") or ""
    if not message.strip():
        return 0

    violations = find_violations(message)
    if not violations:
        return 0

    if already_blocked(payload.get("prompt_id", "")):
        print(
            "simple-english: still violating after one retry, allowing through. "
            + "; ".join(violations),
            file=sys.stderr,
        )
        return 0

    advice = long_sentences(message)
    lines = ["Your reply breaks the simple-english output style. Rewrite it."]
    lines += [f"  - {v}" for v in violations]
    if advice:
        lines.append(f"  - advisory, {len(advice)} sentence(s) over 25 words:")
        lines += [f"      {a}" for a in advice[:3]]
    lines.append("Keep the same facts. Change only the wording.")
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
