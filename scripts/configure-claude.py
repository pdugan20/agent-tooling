#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import tempfile
from pathlib import Path

OFFICIAL_SUPERPOWERS = "superpowers@claude-plugins-official"
CONFIGURED_SUPERPOWERS = "superpowers@superpowers-configured"
EXPLICIT_PERSONAL_SKILLS = ("review-animations",)
# ASD-STE100 Simplified Technical English. Applies to every response the main
# agent writes, in every session, with no invocation. See
# global/output-styles/simple-english.md and docs/output-styles.md.
OUTPUT_STYLE = "simple-english"
RETIRED_SKILLS = (
    "execute-plan",
    "formal-spec",
    "production-hardening",
    "strict-tdd",
    "write-plan",
)
# The hook supplies AGENTS.md only when native Claude loading does not apply.
# See its version and project-file checks before adding compatibility shims.
# See global/hooks/agents_md_context.py.
AGENTS_MD_HOOK = Path(__file__).resolve().parents[1] / "global/hooks/agents_md_context.py"
AGENTS_MD_HOOK_MATCHER = "startup|clear|compact"
# Checks an agent's git push against the branch's real base. See
# global/hooks/agent_push_scope.py. It fetches the base, so it gets a longer timeout.
PUSH_SCOPE_HOOK = Path(__file__).resolve().parents[1] / "global/hooks/agent_push_scope.py"
PUSH_SCOPE_HOOK_MATCHER = "Bash"
PUSH_SCOPE_HOOK_TIMEOUT = 30


def ensure_hook(
    data: dict[str, object], event: str, matcher: str, hook_path: Path, timeout: int
) -> None:
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks must be a JSON object")
    groups = hooks.setdefault(event, [])
    if not isinstance(groups, list):
        raise ValueError(f"hooks.{event} must be a JSON array")

    # Drop earlier copies, including ones that point at a previous checkout path.
    def is_managed(group: object) -> bool:
        return isinstance(group, dict) and any(
            isinstance(hook, dict) and hook_path.name in str(hook.get("command", ""))
            for hook in group.get("hooks", [])
        )

    groups[:] = [group for group in groups if not is_managed(group)]
    groups.append(
        {
            "matcher": matcher,
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {shlex.quote(str(hook_path))}",
                    "timeout": timeout,
                }
            ],
        }
    )


def ensure_agents_md_hook(data: dict[str, object], hook_path: Path) -> None:
    ensure_hook(data, "SessionStart", AGENTS_MD_HOOK_MATCHER, hook_path, 10)


def ensure_push_scope_hook(data: dict[str, object], hook_path: Path) -> None:
    ensure_hook(data, "PreToolUse", PUSH_SCOPE_HOOK_MATCHER, hook_path, PUSH_SCOPE_HOOK_TIMEOUT)


def update_settings(
    data: dict[str, object],
    agents_md_hook: Path = AGENTS_MD_HOOK,
    push_scope_hook: Path = PUSH_SCOPE_HOOK,
) -> dict[str, object]:
    existing_plugins = data.get("enabledPlugins", {})
    if isinstance(existing_plugins, dict) and existing_plugins.get(OFFICIAL_SUPERPOWERS) is True:
        raise ValueError(
            "Official Superpowers is enabled. Existing settings were preserved; "
            "review the conflict with the configured fork before rerunning."
        )
    plugins = data.setdefault("enabledPlugins", {})
    overrides = data.setdefault("skillOverrides", {})
    if not isinstance(plugins, dict) or not isinstance(overrides, dict):
        raise ValueError("enabledPlugins and skillOverrides must be JSON objects")

    data["outputStyle"] = OUTPUT_STYLE
    plugins[CONFIGURED_SUPERPOWERS] = True
    for skill in EXPLICIT_PERSONAL_SKILLS:
        overrides[skill] = "user-invocable-only"
    for skill in RETIRED_SKILLS:
        overrides.pop(skill, None)
    ensure_agents_md_hook(data, agents_md_hook)
    ensure_push_scope_hook(data, push_scope_hook)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.settings.read_text()) if args.settings.exists() else {}
    try:
        update_settings(data)
    except ValueError as error:
        parser.error(str(error))

    rendered = json.dumps(data, indent=2) + "\n"
    if args.dry_run:
        print(rendered, end="")
        return

    args.settings.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        dir=args.settings.parent,
        prefix=f".{args.settings.name}.",
        text=True,
    )
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(rendered)
        os.replace(temporary, args.settings)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == "__main__":
    main()
