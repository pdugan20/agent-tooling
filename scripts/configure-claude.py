#!/usr/bin/env python3

import argparse
import json
import os
import tempfile
from pathlib import Path


PLUGIN = "superpowers@claude-plugins-official"
DELIVERY_SKILLS = (
    "execute-plan",
    "formal-spec",
    "production-hardening",
    "review-animations",
    "strict-tdd",
    "write-plan",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.settings.read_text()) if args.settings.exists() else {}
    plugins = data.setdefault("enabledPlugins", {})
    overrides = data.setdefault("skillOverrides", {})

    plugins[PLUGIN] = False
    for skill in DELIVERY_SKILLS:
        overrides[skill] = "user-invocable-only"

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
