#!/usr/bin/env python3

"""List enabled user-scoped Claude plugins not declared in the canonical manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def desired_plugin_ids(manifest: Path) -> set[str]:
    return {
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def undeclared_enabled_plugins(plugins: list[dict[str, Any]], desired: set[str]) -> list[str]:
    return sorted(
        plugin_id
        for plugin in plugins
        if plugin.get("scope") == "user"
        and plugin.get("enabled")
        and (plugin_id := plugin.get("id"))
        and not plugin_id.endswith("@skills-dir")
        and plugin_id not in desired
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    plugins = json.load(sys.stdin)
    if not isinstance(plugins, list):
        raise SystemExit("Claude plugin listing must be a JSON array")

    for plugin_id in undeclared_enabled_plugins(plugins, desired_plugin_ids(args.manifest)):
        print(plugin_id)


if __name__ == "__main__":
    main()
