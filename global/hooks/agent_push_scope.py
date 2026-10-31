#!/usr/bin/env python3
"""PreToolUse hook that checks an agent's git push against its real base.

Agents stack branches, merge base branches forward, and resolve conflicts by
taking a whole file. Each of those can carry CI, build-toolchain, or
package-script changes into a pull request that never meant to make them, and
the pull request's own checks then run the carried configuration. This hook runs
before an agent's shell tool executes a git push. It compares each pushed branch
with its real base (the pull request's base when one exists, otherwise the
remote default branch) and denies the push when:

- the three-dot diff touches a guarded area the branch has not declared:
  ci-config (.circleci/, .github/workflows/, .github/actions/), buildkit (any
  path inside a buildkit directory), ci-tool-versions (ci-tool-versions.env), or
  package-scripts (a change to the "scripts" object of any package.json outside
  the vendored skill snapshots under .agents/skills/); or
- the pull request sits more than MAX_STACK_DEPTH levels above the default
  branch.

A branch declares intent with an "Agent-Scope:" line in a commit message on the
branch or in the pull request body, for example
"Agent-Scope: ci-config, package-scripts".

The hook is registered for agent shell tools only. People running git in a
terminal never reach it, and a command without "git" and "push" returns before
any subprocess runs. It never executes the supplied command. It allows the push
when it cannot read the repository, so a broken environment never blocks work.
This is a guardrail, not a security boundary: scripts, aliases, and dynamic
shell expansion are not interpreted.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import PurePosixPath

MAX_STACK_DEPTH = 2
SHELL_TOOLS = ("Bash", "exec_command", "shell", "shell_command", "functions.exec_command")
SCOPES = ("ci-config", "buildkit", "ci-tool-versions", "package-scripts")
SCOPE_LINE = re.compile(r"(?im)^\s*Agent-Scope:\s*(.+?)\s*$")
CI_PREFIXES = (".circleci/", ".github/workflows/", ".github/actions/")
# Skill snapshots are installed verbatim by the Skills CLI and never run as this
# repository's packages, so their package.json scripts are not package-scripts.
SKILL_SNAPSHOT_PREFIX = ".agents/skills/"
GIT_TIMEOUT = 5
FETCH_TIMEOUT = 15
GH_TIMEOUT = 8
PUSH_SKIP_FLAGS = ("--delete", "-d", "--tags", "--all", "--mirror", "--prune")
PUSH_VALUED = ("--repo", "--receive-pack", "--exec", "-o", "--push-option", "--recurse-submodules")


@dataclass
class Push:
    cwd: str
    remote: str = "origin"
    refspecs: list[str] = field(default_factory=list)


def run(args: list[str], cwd: str, timeout: int = GIT_TIMEOUT) -> str | None:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def git_push(args: list[str], cwd: str) -> Push | None:
    while args and args[0].startswith("-"):
        option = args.pop(0)
        if option in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"):
            value = args.pop(0) if args else ""
            if option == "-C":
                cwd = os.path.abspath(os.path.join(cwd, os.path.expanduser(value)))
        elif option.startswith("-C") and len(option) > 2:
            cwd = os.path.abspath(os.path.join(cwd, option[2:]))
    if not args or args[0] != "push":
        return None
    args = args[1:]
    if any(arg in PUSH_SKIP_FLAGS for arg in args):
        return None
    positional: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            positional.extend(args[index + 1 :])
            break
        if arg in PUSH_VALUED:
            index += 2
            continue
        if not arg.startswith("-"):
            positional.append(arg)
        index += 1
    push = Push(cwd=cwd)
    if positional:
        push.remote = positional[0]
        push.refspecs = positional[1:]
    return push


def find_pushes(command: str, cwd: str, depth: int = 0) -> list[Push]:
    if depth > 3:
        return []
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return []
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token and all(char in ";&|()\n" for char in token):
            segments.append([])
        else:
            segments[-1].append(token)
    pushes: list[Push] = []
    for words in segments:
        while words and (
            re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0])
            or words[0] in ("command", "exec", "env", "then", "do", "if", "!", "time")
        ):
            words = words[1:]
        if not words:
            continue
        program = os.path.basename(words[0])
        if program == "cd" and len(words) == 2:
            cwd = os.path.abspath(os.path.join(cwd, os.path.expanduser(words[1])))
        elif program == "git":
            push = git_push(list(words[1:]), cwd)
            if push:
                pushes.append(push)
        elif program in ("bash", "zsh", "sh"):
            for index, arg in enumerate(words[1:], 1):
                if arg.startswith("-") and "c" in arg and index + 1 < len(words):
                    pushes.extend(find_pushes(words[index + 1], cwd, depth + 1))
                    break
    return pushes


def default_branch(cwd: str, remote: str) -> str | None:
    head = run(["git", "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD"], cwd)
    if head:
        return head.strip().removeprefix(f"refs/remotes/{remote}/")
    for name in ("main", "master"):
        if run(["git", "rev-parse", "--verify", "--quiet", f"refs/remotes/{remote}/{name}"], cwd):
            return name
    return None


def pull_request(cwd: str, branch: str) -> dict | None:
    output = run(
        ["gh", "pr", "view", branch, "--json", "number,baseRefName,body,state"], cwd, GH_TIMEOUT
    )
    if not output:
        return None
    try:
        data = json.loads(output)
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("state") == "OPEN" else None


def stack_depth(cwd: str, base: str, default: str) -> int:
    """Count open pull requests from this one down to the default branch."""
    depth = 1
    seen = {base}
    while base != default and depth <= MAX_STACK_DEPTH:
        depth += 1
        parent = pull_request(cwd, base)
        if not parent:
            break
        base = parent.get("baseRefName") or default
        if base in seen:
            break
        seen.add(base)
    return depth


def changed_scripts(cwd: str, merge_base: str, head: str, path: str) -> list[str]:
    def scripts(revision: str) -> dict:
        raw = run(["git", "show", f"{revision}:{path}"], cwd)
        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            return {}
        value = data.get("scripts") if isinstance(data, dict) else None
        return value if isinstance(value, dict) else {}

    before, after = scripts(merge_base), scripts(head)
    return sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))


def classify(path: str) -> str | None:
    pure = PurePosixPath(path)
    if pure.name == "ci-tool-versions.env":
        return "ci-tool-versions"
    if any("buildkit" in part.lower() for part in pure.parts[:-1]):
        return "buildkit"
    if path.startswith(CI_PREFIXES):
        return "ci-config"
    return None


def declared_scopes(cwd: str, merge_base: str, head: str, body: str) -> set[str]:
    log = run(["git", "log", "--format=%B", f"{merge_base}..{head}"], cwd) or ""
    declared: set[str] = set()
    for text in (log, body or ""):
        for match in SCOPE_LINE.finditer(text):
            declared.update(part.strip().lower() for part in re.split(r"[,\s]+", match.group(1)))
    return declared & set(SCOPES)


def resolve_refspec(push: Push, refspec: str | None) -> tuple[str, str] | None:
    """Return the local source revision and the remote branch name."""
    spec = (refspec or "HEAD").lstrip("+")
    source, _, destination = spec.partition(":")
    if not source or source.startswith("refs/tags/"):
        return None
    if not destination:
        destination = source
    if destination == "HEAD":
        current = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], push.cwd)
        if not current:
            return None
        destination = current.strip()
    destination = destination.removeprefix("refs/heads/")
    if destination.startswith("refs/"):
        return None
    return source, destination


def describe(undeclared: dict[str, list[str]]) -> str:
    lines = []
    for scope in SCOPES:
        items = undeclared.get(scope)
        if items:
            more = f"; and {len(items) - 5} more" if len(items) > 5 else ""
            lines.append(f"  {scope}: {'; '.join(items[:5])}{more}")
    return "\n".join(lines)


def problems_for(push: Push, refspec: str | None) -> list[str]:
    resolved = resolve_refspec(push, refspec)
    if not resolved:
        return []
    source, branch = resolved
    head = run(["git", "rev-parse", "--verify", "--quiet", f"{source}^{{commit}}"], push.cwd)
    default = default_branch(push.cwd, push.remote)
    if not head or not default or branch == default:
        return []
    head = head.strip()

    pr = pull_request(push.cwd, branch)
    base = (pr or {}).get("baseRefName") or default
    run(["git", "fetch", "--quiet", "--no-tags", push.remote, base], push.cwd, FETCH_TIMEOUT)
    merge_base = run(["git", "merge-base", f"refs/remotes/{push.remote}/{base}", head], push.cwd)
    if not merge_base:
        return []
    merge_base = merge_base.strip()

    problems: list[str] = []
    if pr:
        depth = stack_depth(push.cwd, base, default)
        if depth > MAX_STACK_DEPTH:
            problems.append(
                f"{branch} is stacked at least {depth} pull requests above {default}; the limit "
                f"is {MAX_STACK_DEPTH}. Land or fold the lower branches, then rebuild this one "
                f"on {default} plus its own change."
            )

    diff = run(["git", "diff", "--name-only", f"{merge_base}...{head}"], push.cwd) or ""
    found: dict[str, list[str]] = {}
    for path in diff.splitlines():
        scope = classify(path)
        if scope:
            found.setdefault(scope, []).append(path)
        if PurePosixPath(path).name == "package.json" and not path.startswith(
            SKILL_SNAPSHOT_PREFIX
        ):
            keys = changed_scripts(push.cwd, merge_base, head, path)
            if keys:
                found.setdefault("package-scripts", []).append(f"{path} ({', '.join(keys)})")

    declared = declared_scopes(push.cwd, merge_base, head, (pr or {}).get("body") or "")
    undeclared = {scope: items for scope, items in found.items() if scope not in declared}
    if undeclared:
        names = ", ".join(scope for scope in SCOPES if scope in undeclared)
        problems.append(
            f"{branch} changes guarded areas compared with {push.remote}/{base} that the branch "
            f"does not declare:\n{describe(undeclared)}\n"
            f"If a change is unintended, rebuild the branch as {base} plus its own diff. If it "
            f"is intended, add 'Agent-Scope: {names}' to a commit message on the branch or as a "
            "line in the pull request body, then push again."
        )
    return problems


def check(event: dict) -> str | None:
    if event.get("tool_name", "") not in SHELL_TOOLS:
        return None
    args = event.get("tool_input", {})
    if not isinstance(args, dict):
        return None
    command = args.get("command", args.get("cmd", ""))
    if isinstance(command, list):
        command = shlex.join(str(part) for part in command)
    if not isinstance(command, str) or "git" not in command or "push" not in command:
        return None
    cwd = os.path.expanduser(args.get("workdir") or event.get("cwd") or os.getcwd())
    problems: list[str] = []
    for push in find_pushes(command, cwd):
        for refspec in push.refspecs or [None]:
            problems.extend(problems_for(push, refspec))
    if not problems:
        return None
    return "Agent push scope check refused this push.\n" + "\n".join(problems)


def main() -> int:
    try:
        reason = check(json.load(sys.stdin))
    except Exception as error:  # a hook failure must never block work
        print(f"Agent push scope check skipped: {error}", file=sys.stderr)
        return 0
    if reason:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
