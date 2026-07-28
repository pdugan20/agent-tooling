#!/usr/bin/env python3

"""Generate the portable catalog and optional machine-local runtime snapshot."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CATALOG_ROOT = ROOT / "catalog"
CATALOG_DATA = CATALOG_ROOT / "data.json"
RUNTIME_DATA = CATALOG_ROOT / "runtime-data.local.json"
PLUGIN_METADATA = CATALOG_ROOT / "plugin-metadata.json"

SKILL_PRIORITY = {
    "feature-delivery": 1,
    "code-native-ui-ideation": 2,
    "swiftui-pro": 3,
    "apple-design": 4,
    "review-animations": 5,
    "animation-vocabulary": 6,
    "emil-design-eng": 7,
    "production-hardening": 20,
}


class CatalogError(Exception):
    """Raised when canonical catalog inputs are incomplete or invalid."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise CatalogError(f"{path.relative_to(ROOT)} has no YAML frontmatter")

    block = text[4 : text.index("\n---\n", 4)]
    result: dict[str, str] = {}
    for line in block.splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def read_plugin_entries(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def read_skill_version(path: Path) -> str:
    match = re.search(r'(?m)^\s+version:\s*["\']?([^"\'\s]+)', path.read_text(encoding="utf-8"))
    return match.group(1) if match else "Git"


def humanize_name(name: str) -> str:
    special_names = {"figma": "Figma", "github": "GitHub", "swiftui": "SwiftUI"}
    return " ".join(
        special_names.get(part, part.upper() if len(part) <= 3 else part.title())
        for part in name.split("-")
    )


def read_skill_interface(skill_root: Path) -> tuple[str | None, str | None, str]:
    agents_manifest = skill_root / "agents/openai.yaml"
    if not agents_manifest.exists():
        return None, None, "Automatic"

    text = agents_manifest.read_text(encoding="utf-8")
    display_name_match = re.search(r'(?m)^\s+display_name:\s*["\']?(.+?)["\']?\s*$', text)
    description_match = re.search(r'(?m)^\s+short_description:\s*["\']?(.+?)["\']?\s*$', text)
    implicit_match = re.search(r"(?m)^\s+allow_implicit_invocation:\s*(true|false)\s*$", text)
    display_name = display_name_match.group(1).strip("\"'") if display_name_match else None
    description = description_match.group(1).strip("\"'") if description_match else None
    invocation = (
        "Automatic" if implicit_match is None or implicit_match.group(1) == "true" else "Explicit"
    )
    return display_name, description, invocation


def skill_item(skill_path: Path) -> dict[str, Any]:
    skill_root = skill_path.parent
    frontmatter = read_frontmatter(skill_path)
    name = frontmatter.get("name")
    if not name or name != skill_root.name:
        raise CatalogError(f"{skill_path.relative_to(ROOT)} name must match its directory")

    display_name, short_description, invocation = read_skill_interface(skill_root)
    return {
        "description": short_description or frontmatter.get("description", ""),
        "displayName": display_name or humanize_name(name),
        "featured": SKILL_PRIORITY.get(name, 50),
        "id": f"skill:{name}",
        "invocation": invocation,
        "name": name,
        "path": skill_path.relative_to(ROOT).as_posix(),
        "runtimes": ["codex", "claude"],
        "source": "personal",
        "sourceLabel": "Built here",
        "state": "Configured",
        "type": "skill",
        "version": read_skill_version(skill_path),
    }


def plugin_item(
    plugin_id: str,
    runtime: str,
    metadata: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    name, _marketplace = plugin_id.split("@", 1)
    return {
        "description": metadata["description"],
        "displayName": metadata.get("displayName", humanize_name(name)),
        "featured": 100 + index,
        "id": f"plugin:{runtime}:{plugin_id}",
        "invocation": None,
        "name": name,
        "path": metadata.get("path", f"config/{runtime}-plugins.txt"),
        "pluginId": plugin_id,
        "runtimes": [runtime],
        "source": metadata["source"],
        "sourceLabel": metadata["sourceLabel"],
        "state": "Configured",
        "type": "plugin",
        "version": metadata.get("version", "Managed"),
    }


def build_catalog() -> dict[str, Any]:
    plugin_metadata = load_json(PLUGIN_METADATA)

    skill_items = [skill_item(path) for path in sorted((ROOT / "skills").glob("*/SKILL.md"))]

    configured: list[tuple[str, str]] = []
    for runtime in ("codex", "claude"):
        manifest_path = ROOT / f"config/{runtime}-plugins.txt"
        configured.extend((plugin_id, runtime) for plugin_id in read_plugin_entries(manifest_path))

    configured_ids = {plugin_id for plugin_id, _runtime in configured}
    metadata_ids = set(plugin_metadata)
    if configured_ids != metadata_ids:
        missing = sorted(configured_ids - metadata_ids)
        stale = sorted(metadata_ids - configured_ids)
        raise CatalogError(f"plugin metadata mismatch; missing={missing}, stale={stale}")

    plugin_items = [
        plugin_item(plugin_id, runtime, plugin_metadata[plugin_id], index)
        for index, (plugin_id, runtime) in enumerate(configured)
    ]
    items = sorted(skill_items + plugin_items, key=lambda item: (item["featured"], item["name"]))
    return {
        "generatedFrom": [
            "skills/*/SKILL.md",
            "config/superpowers.json",
            "config/codex-plugins.txt",
            "config/claude-plugins.txt",
            "catalog/plugin-metadata.json",
        ],
        "items": items,
        "schemaVersion": 1,
    }


def source_details(plugin_id: str, metadata: dict[str, Any]) -> tuple[str, str]:
    if plugin_id in metadata:
        item = metadata[plugin_id]
        return item["source"], item["sourceLabel"]

    marketplace = plugin_id.rsplit("@", 1)[-1]
    if marketplace.startswith("openai-"):
        return "openai", marketplace.replace("-", " ").title()
    if marketplace == "claude-plugins-official":
        return "anthropic", "Anthropic official"
    if marketplace == "personal":
        return "personal", "Personal"
    return "third-party", marketplace.replace("-", " ").title()


def run_json_command(command: list[str]) -> Any:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def build_runtime_snapshot() -> dict[str, Any]:
    canonical = build_catalog()
    canonical_skills = [item for item in canonical["items"] if item["type"] == "skill"]
    plugin_metadata = load_json(PLUGIN_METADATA)
    desired_ids = {
        (item["pluginId"], item["runtimes"][0]): item
        for item in canonical["items"]
        if item["type"] == "plugin"
    }
    items: list[dict[str, Any]] = []
    codex_data = run_json_command(["codex", "plugin", "list", "--json"])
    for skill in canonical_skills:
        installed_runtimes = []
        if (Path.home() / ".agents/skills" / skill["name"] / "SKILL.md").exists():
            installed_runtimes.append("codex")
        if (Path.home() / ".claude/skills" / skill["name"] / "SKILL.md").exists():
            installed_runtimes.append("claude")
        if installed_runtimes:
            runtime_skill = dict(skill)
            runtime_skill["runtimes"] = installed_runtimes
            runtime_skill["state"] = "Installed"
            items.append(runtime_skill)

    for index, plugin in enumerate(codex_data.get("installed", [])):
        plugin_id = plugin["pluginId"]
        source, source_label = source_details(plugin_id, plugin_metadata)
        desired = desired_ids.get((plugin_id, "codex"))
        items.append(
            {
                "description": (
                    desired["description"]
                    if desired
                    else f"Installed Codex plugin from {source_label}."
                ),
                "displayName": desired["displayName"] if desired else humanize_name(plugin["name"]),
                "featured": 200 + (0 if desired else 100) + index,
                "id": f"runtime:codex:{plugin_id}",
                "invocation": None,
                "name": plugin["name"],
                "path": desired["path"] if desired else None,
                "pluginId": plugin_id,
                "runtimes": ["codex"],
                "source": source,
                "sourceLabel": source_label,
                "state": "Enabled" if plugin.get("enabled") else "Disabled",
                "type": "plugin",
                "version": plugin.get("version") or "Unknown",
            }
        )

    claude_data = run_json_command(["claude", "plugin", "list", "--json"])
    user_plugins = [plugin for plugin in claude_data if plugin.get("scope") == "user"]
    for index, plugin in enumerate(user_plugins):
        plugin_id = plugin["id"]
        source, source_label = source_details(plugin_id, plugin_metadata)
        desired = desired_ids.get((plugin_id, "claude"))
        items.append(
            {
                "description": (
                    desired["description"]
                    if desired
                    else f"Installed Claude plugin from {source_label}."
                ),
                "displayName": (
                    desired["displayName"] if desired else humanize_name(plugin_id.split("@", 1)[0])
                ),
                "featured": 400 + (0 if desired else 100) + index,
                "id": f"runtime:claude:{plugin_id}",
                "invocation": None,
                "name": plugin_id.split("@", 1)[0],
                "path": desired["path"] if desired else None,
                "pluginId": plugin_id,
                "runtimes": ["claude"],
                "source": source,
                "sourceLabel": source_label,
                "state": "Enabled" if plugin.get("enabled") else "Disabled",
                "type": "plugin",
                "version": plugin.get("version") or "Unknown",
            }
        )

    return {
        "generatedAt": datetime.now(UTC).isoformat(),
        "items": items,
        "message": "What Codex and Claude currently report as installed on this computer.",
        "schemaVersion": 1,
    }


def rendered_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def write_or_check_catalog(*, check: bool) -> None:
    expected = rendered_json(build_catalog())
    if check:
        actual = CATALOG_DATA.read_text(encoding="utf-8") if CATALOG_DATA.exists() else ""
        if actual != expected:
            raise CatalogError("catalog/data.json is stale; run npm run catalog:generate")
        print("Generated catalog data is current.")
        return
    CATALOG_DATA.write_text(expected, encoding="utf-8")
    print(f"Generated {CATALOG_DATA.relative_to(ROOT)}.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--snapshot-runtime", action="store_true")
    args = parser.parse_args()

    try:
        write_or_check_catalog(check=args.check)
        if args.snapshot_runtime:
            RUNTIME_DATA.write_text(rendered_json(build_runtime_snapshot()), encoding="utf-8")
            print(f"Generated private snapshot {RUNTIME_DATA.relative_to(ROOT)}.")
            print("Open /catalog/?runtime=local and choose This Mac to view it.")
    except (CatalogError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Catalog generation failed: {error}") from error


if __name__ == "__main__":
    main()
