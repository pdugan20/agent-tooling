#!/usr/bin/env python3
"""Update the skills each repository locks in skills-lock.json, one reviewed PR per repository.

The targets file lists the repositories to visit. Each run clones every target's
default branch into a temporary directory, updates its locked skills with the
official Skills CLI and opens one pull request with the changes. A pull request
is set to auto-merge only when every changed skill passes the rules below and the
repository requires status checks. Otherwise it waits for review.

A changed skill can merge without review when its source is trusted, or when:

- every changed file is Markdown,
- it adds no URL and no line inside a shell code block, and
- its upstream change is at least COOLDOWN_DAYS old.

Targets in "report" mode are checked the same way, but nothing is pushed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

SKILLS_CLI = "skills@1.7.4"
COOLDOWN_DAYS = 7
PLUGIN_STALE_DAYS = 30
SHELL_FENCE_LANGUAGES = {"bash", "sh", "shell", "zsh", "console", "fish", "terminal"}
FENCE_RE = re.compile(r"^\s*(\x60{3,}|~{3,})\s*([\w+-]*)")
URL_RE = re.compile(r"https?://[^\s)>\]\"'\x60]+")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")
DEFAULT_TARGETS = Path.home() / ".codex/local/skill-update-targets.json"
DEFAULT_RECEIPTS = Path.home() / ".codex/local/skill-updates"


class UpdateError(RuntimeError):
    """Raised when a target cannot be checked or updated safely."""


@dataclass
class SkillChange:
    name: str
    source: str
    old_ref: str | None
    new_ref: str | None
    upstream_date: str | None
    review_reasons: list[str] = field(default_factory=list)


def run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", **(env or {})},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()[-1:]
        raise UpdateError(f"{command[0]} {command[1] if len(command) > 1 else ''} failed: {detail}")
    return result.stdout


def gh_token(user: str) -> str:
    return run(["gh", "auth", "token", "--user", user]).strip()


def gh_api(path: str, token: str) -> object:
    return json.loads(run(["gh", "api", path], env={"GH_TOKEN": token}))


def shell_lines(text: str) -> set[str]:
    """Return the non-blank lines inside shell-language fenced code blocks."""
    lines: set[str] = set()
    fence: str | None = None
    in_shell = False
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if fence is None and match:
            fence = match.group(1)[0]
            in_shell = match.group(2).lower() in SHELL_FENCE_LANGUAGES
            continue
        if fence is not None and line.strip().startswith(fence * 3):
            fence = None
            in_shell = False
            continue
        if in_shell and line.strip():
            lines.add(line.strip())
    return lines


def review_reasons(files: list[tuple[str, str | None, str | None]]) -> list[str]:
    """Explain why a skill's file changes need review. Each file is (path, old, new)."""
    not_markdown, urls, commands = [], [], []
    for path, old, new in files:
        if new is None:
            continue
        if not path.lower().endswith(".md"):
            not_markdown.append(path)
            continue
        if set(URL_RE.findall(new)) - set(URL_RE.findall(old or "")):
            urls.append(path)
        if shell_lines(new) - shell_lines(old or ""):
            commands.append(path)
    reasons = []
    for paths, what in (
        (not_markdown, "changes files that aren't Markdown"),
        (urls, "adds URLs"),
        (commands, "adds shell commands"),
    ):
        if paths:
            shown = ", ".join(Path(path).name for path in paths[:3])
            more = f" and {len(paths) - 3} more" if len(paths) > 3 else ""
            reasons.append(f"{what} ({shown}{more})")
    return reasons


def parse_version(tag: str) -> tuple[int, int, int] | None:
    match = VERSION_RE.match(tag)
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def newest_tag(tags: list[str], current: str) -> str | None:
    """Return the highest version tag above current, keeping its v prefix style."""
    current_version = parse_version(current)
    if current_version is None:
        return None
    prefixed = current.startswith("v")
    candidates = [
        tag
        for tag in tags
        if tag.startswith("v") == prefixed and (parse_version(tag) or (0, 0, 0)) > current_version
    ]
    return max(candidates, key=lambda tag: parse_version(tag) or (0, 0, 0), default=None)


def old_enough(date: str | None, now: datetime) -> bool:
    if date is None:
        return False
    changed = datetime.fromisoformat(date.replace("Z", "+00:00"))
    return now - changed >= timedelta(days=COOLDOWN_DAYS)


def skill_directory(entry: dict) -> str:
    return str(Path(entry["skillPath"]).parent)


def upstream_path_date(source: str, path: str, ref: str | None, token: str) -> str | None:
    query = f"repos/{source}/commits?path={path}&per_page=1" + (f"&sha={ref}" if ref else "")
    commits = gh_api(query, token)
    if not isinstance(commits, list) or not commits:
        return None
    return commits[0]["commit"]["committer"]["date"]


def status_paths(output: str) -> list[str]:
    """Paths from NUL-separated `git status --porcelain -z` output, without Git's quoting."""
    entries = output.split("\0")
    paths = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if entry[0] in "RC":
            # A rename or copy is followed by its original path, which no longer exists.
            index += 1
    return paths


def changed_files(checkout: Path, skill: str) -> list[tuple[str, str | None, str | None]]:
    root = f".agents/skills/{skill}"
    status = run(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all", "--", root], checkout
    )
    files = []
    for path in status_paths(status):
        new_path = checkout / path
        if new_path.is_symlink() or (new_path.exists() and not new_path.is_file()):
            # A link or special file is never treated as plain Markdown.
            files.append((f"{path} (link or special file)", None, ""))
            continue
        if not path.lower().endswith(".md"):
            # Only Markdown content is inspected, so other files, including binaries, aren't read.
            files.append((path, None, "" if new_path.exists() else None))
            continue
        old = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=checkout, capture_output=True)
        files.append(
            (
                path,
                old.stdout.decode(errors="replace") if old.returncode == 0 else None,
                new_path.read_text(errors="replace") if new_path.is_file() else None,
            )
        )
    return files


def revert_skill(checkout: Path, skill: str) -> None:
    """Put a skill's installed files back as committed, removing anything the update added."""
    for root in (f".agents/skills/{skill}", f".claude/skills/{skill}"):
        if run(["git", "ls-files", root], checkout).strip():
            run(["git", "checkout", "HEAD", "--", root], checkout)
        run(["git", "clean", "-fdq", "--", root], checkout)


def update_target(target: dict, config: dict, now: datetime, dry_run: bool) -> dict:
    repo = target["repository"]
    token = gh_token(target["githubUser"])
    trusted = set(config.get("trustedSources", []))
    with tempfile.TemporaryDirectory(prefix="skill-update-") as temporary:
        checkout = Path(temporary) / "repo"
        run(["git", "clone", "--quiet", "--depth", "1", target["cloneUrl"], str(checkout)])
        lock_path = checkout / "skills-lock.json"
        original_lock = json.loads(lock_path.read_text())
        original = original_lock["skills"]
        agents = ["codex"] + (["claude-code"] if (checkout / ".claude/skills").is_dir() else [])
        npx = ["npx", "--yes", SKILLS_CLI]

        run([*npx, "update", "-p", "-y"], checkout)
        notes: list[str] = []
        for name, entry in original.items():
            ref = entry.get("ref")
            if not ref or SHA_RE.match(ref):
                continue
            tags = [
                tag["name"] for tag in gh_api(f"repos/{entry['source']}/tags?per_page=100", token)
            ]
            tag = newest_tag(tags, ref)
            if tag is None:
                continue
            url = f"https://github.com/{entry['source']}/tree/{tag}/{skill_directory(entry)}"
            try:
                run([*npx, "add", url, "--agent", *agents, "--skill", name, "-y"], checkout)
            except UpdateError:
                notes.append(
                    f"{name} has a newer release, {tag}, but the skill isn't at the same path "
                    "there. It may have been renamed or moved, so update it by hand"
                )

        updated = json.loads(lock_path.read_text())["skills"]
        changes: list[SkillChange] = []
        drifted: list[str] = []
        for name, entry in original.items():
            new_entry = updated.get(name, entry)
            committed = bool(run(["git", "ls-files", f".agents/skills/{name}"], checkout).strip())
            if not committed:
                if new_entry != entry:
                    drifted.append(name)
                    if target["mode"] == "pr":
                        notes.append(
                            f"{name} changed upstream, but its files aren't committed at "
                            ".agents/skills, so the change can't be reviewed in a pull request"
                        )
                updated[name] = entry
                revert_skill(checkout, name)
                continue
            files = changed_files(checkout, name)
            if not files and new_entry == entry:
                if entry.get("ref") and SHA_RE.match(entry["ref"]):
                    latest = upstream_path_date(
                        entry["source"], skill_directory(entry), None, token
                    )
                    pinned = upstream_path_date(
                        entry["source"], skill_directory(entry), entry["ref"], token
                    )
                    if latest and pinned and latest > pinned:
                        notes.append(f"{name} is pinned to a commit and upstream has newer changes")
                continue
            new_ref = new_entry.get("ref")
            date = upstream_path_date(entry["source"], skill_directory(entry), new_ref, token)
            if not old_enough(date, now):
                revert_skill(checkout, name)
                updated[name] = entry
                notes.append(f"{name} changed upstream less than {COOLDOWN_DAYS} days ago")
                continue
            reasons = [] if entry["source"] in trusted else review_reasons(files)
            changes.append(
                SkillChange(name, entry["source"], entry.get("ref"), new_ref, date, reasons)
            )

        updated_lock = {**original_lock, "skills": updated}
        lock_path.write_text(json.dumps(updated_lock, indent=2) + "\n")
        result = {
            "repository": repo,
            "mode": target["mode"],
            "changes": [change.__dict__ for change in changes],
            "notes": notes,
        }
        if drifted:
            result["changedUpstream"] = drifted
        if not changes:
            result["status"] = "drift-reported" if drifted else "current"
            return result
        if target["mode"] != "pr" or dry_run:
            result["status"] = "drift-reported"
            return result
        for command in target.get("postUpdate", []):
            run(command, checkout)
        return open_pull_request(target, token, checkout, changes, result, now)


def open_pull_request(
    target: dict,
    token: str,
    checkout: Path,
    changes: list[SkillChange],
    result: dict,
    now: datetime,
) -> dict:
    repo = target["repository"]
    branch = f"chore/update-locked-skills-{now:%Y-%m}"
    run(["git", "switch", "--quiet", "-c", branch], checkout)
    # Stage only the skills that were assessed, so nothing unclassified reaches the pull request.
    paths = ["skills-lock.json", *target.get("extraPaths", [])]
    for change in changes:
        paths.append(f".agents/skills/{change.name}")
        if (checkout / ".claude/skills" / change.name).is_symlink():
            paths.append(f".claude/skills/{change.name}")
    run(["git", "add", "-A", "--", *paths], checkout)
    title = target.get("title", "chore(skills): update locked skills")
    run(["git", "commit", "--quiet", "-m", title], checkout)
    environment = {"GH_TOKEN": token}
    existing = json.loads(
        run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--head",
                branch,
                "--json",
                "url,autoMergeRequest",
            ],
            env=environment,
        )
    )
    # A rerun can bring changes that need review, so turn off auto-merge before replacing the head.
    if existing and existing[0].get("autoMergeRequest"):
        run(["gh", "pr", "merge", existing[0]["url"], "--disable-auto"], env=environment)
    # A rerun in the same month replaces the branch, so lease against its current tip.
    remote = run(["git", "ls-remote", "--heads", "origin", branch], checkout).split()
    lease = f"--force-with-lease={branch}:{remote[0] if remote else ''}"
    run(["git", "push", "--quiet", lease, "origin", branch], checkout)

    rows = []
    for change in changes:
        version = f"{change.old_ref} → {change.new_ref}" if change.new_ref else "latest upstream"
        review = "; ".join(change.review_reasons) if change.review_reasons else "none"
        rows.append(f"| \x60{change.name}\x60 | {change.source} | {version} | {review} |")
    needs_review = [change for change in changes if change.review_reasons]
    settings = gh_api(f"repos/{repo}", token)
    rules = gh_api(f"repos/{repo}/rules/branches/{settings['default_branch']}", token)
    requires_checks = any(rule.get("type") == "required_status_checks" for rule in rules)
    if needs_review:
        merge_note = "Waiting for review because at least one skill needs it."
    elif not requires_checks:
        merge_note = "Waiting for review because this repository has no required checks."
    elif not settings.get("allow_auto_merge"):
        merge_note = "Waiting for review because auto-merge is turned off in this repository."
    else:
        merge_note = "Set to auto-merge once the required checks pass."
    body = "\n".join(
        [
            "Monthly update of the skills locked in \x60skills-lock.json\x60.",
            "",
            "| Skill | Source | Version | Needs review because |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            merge_note,
            "",
            "Review instruction changes like dependency changes before merging by hand.",
        ]
    )
    if existing:
        url = existing[0]["url"]
        run(["gh", "pr", "edit", url, "--body", body], env=environment)
    else:
        url = run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                repo,
                "--head",
                branch,
                "--title",
                title,
                "--body",
                body,
            ],
            env=environment,
        ).strip()
    result["pullRequest"] = url
    if merge_note.startswith("Set to auto-merge"):
        run(["gh", "pr", "merge", url, "--auto", "--squash"], env=environment)
        result["status"] = "auto-merge-enabled"
    else:
        result["status"] = "needs-review"
    result["mergeNote"] = merge_note
    return result


def plugin_freshness(now: datetime) -> list[dict]:
    """List plugin marketplaces that haven't refreshed in PLUGIN_STALE_DAYS."""
    entries: list[tuple[str, str, str]] = []
    codex_config = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"
    if codex_config.is_file():
        for name, value in tomllib.loads(codex_config.read_text()).get("marketplaces", {}).items():
            if isinstance(value, dict) and value.get("last_updated"):
                entries.append(("codex", name, value["last_updated"]))
    claude_marketplaces = Path.home() / ".claude/plugins/known_marketplaces.json"
    if claude_marketplaces.is_file():
        for name, value in json.loads(claude_marketplaces.read_text()).items():
            if isinstance(value, dict) and value.get("lastUpdated"):
                entries.append(("claude", name, value["lastUpdated"]))
    stale = []
    for runtime, name, date in entries:
        updated = datetime.fromisoformat(date.replace("Z", "+00:00"))
        if now - updated >= timedelta(days=PLUGIN_STALE_DAYS):
            stale.append({"runtime": runtime, "marketplace": name, "lastUpdated": date})
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument("--only", action="append", help="Limit the run to this repository.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without pushing.")
    args = parser.parse_args()

    config = json.loads(args.targets.read_text())
    now = datetime.now(UTC)
    results = []
    for target in config["targets"]:
        if args.only and target["repository"] not in args.only:
            continue
        try:
            results.append(update_target(target, config, now, args.dry_run))
        except Exception as error:  # One repository's failure must not stop the others.
            results.append(
                {"repository": target["repository"], "status": "failed", "error": str(error)}
            )
    receipt = {
        "checkedAt": now.isoformat(),
        "results": results,
        "stalePlugins": plugin_freshness(now),
    }
    args.receipts.mkdir(parents=True, exist_ok=True, mode=0o700)
    (args.receipts / f"{now:%Y-%m-%d}.json").write_text(json.dumps(receipt, indent=2) + "\n")
    for result in results:
        line = f"{result['status']}: {result['repository']}"
        if result.get("pullRequest"):
            line += f" {result['pullRequest']}"
        print(line)
        for change in result.get("changes", []):
            print(
                f"  {change['name']}: {'; '.join(change['review_reasons']) or 'no review needed'}"
            )
        if result.get("changedUpstream"):
            print(f"  changed upstream: {', '.join(result['changedUpstream'])}")
        for note in result.get("notes", []):
            print(f"  note: {note}")
        if result.get("error"):
            print(f"  error: {result['error']}")
    for plugin in receipt["stalePlugins"]:
        since = plugin["lastUpdated"]
        print(f"stale plugins: {plugin['runtime']} {plugin['marketplace']} since {since}")
    return 1 if any(result["status"] == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
