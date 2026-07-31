#!/usr/bin/env python3

import argparse
import json
import os
import tempfile
from pathlib import Path

OFFICIAL_SUPERPOWERS = "superpowers@claude-plugins-official"
CONFIGURED_SUPERPOWERS = "superpowers@superpowers-configured"
EXPLICIT_PERSONAL_SKILLS = ("review-animations",)
RETIRED_SKILLS = (
    "execute-plan",
    "formal-spec",
    "production-hardening",
    "strict-tdd",
    "write-plan",
)


def update_settings(data: dict[str, object]) -> dict[str, object]:
    plugins = data.setdefault("enabledPlugins", {})
    overrides = data.setdefault("skillOverrides", {})
    if not isinstance(plugins, dict) or not isinstance(overrides, dict):
        raise ValueError("enabledPlugins and skillOverrides must be JSON objects")

    plugins[OFFICIAL_SUPERPOWERS] = False
    plugins[CONFIGURED_SUPERPOWERS] = True
    for skill in EXPLICIT_PERSONAL_SKILLS:
        overrides[skill] = "user-invocable-only"
    for skill in RETIRED_SKILLS:
        overrides.pop(skill, None)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.settings.read_text()) if args.settings.exists() else {}
    update_settings(data)

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
