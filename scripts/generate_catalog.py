#!/usr/bin/env python3

"""Generate the portable catalog and optional machine-local runtime snapshot."""

from __future__ import annotations

import argparse
import json
import os
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
SKILLS_LOCK = ROOT / "skills-lock.json"
AGENT_TOOLING_REPOSITORY = "https://github.com/pdugan20/agent-tooling"
PATRICK_SKILLS_SOURCE = "pdugan20/skills"

UPSTREAM_SOURCE_LABELS = {
    "emilkowalski/skills": "Emil Kowalski",
    PATRICK_SKILLS_SOURCE: "Pat Dugan",
    "Prisma-Labs-Dev/apple-skills": "Prisma Labs",
    "railwayapp/railway-skills": "Railway",
    "twostraws/swiftui-agent-skill": "Paul Hudson",
}

SKILL_PRIORITY = {
    "feature-delivery": 1,
    "code-native-ui-ideation": 2,
    "production-hardening": 3,
    "scaffold-mintlify-site": 4,
    "review-mintlify-docs": 5,
    "generate-mintlify-reference": 6,
    "write-mintlify-changelog": 7,
    "swiftui-pro": 10,
    "apple-design": 11,
    "review-animations": 12,
    "find-animation-opportunities": 13,
    "animation-vocabulary": 14,
    "emil-design-eng": 15,
    "pick-ui-library": 16,
}


class CatalogError(Exception):
    """Raised when canonical catalog inputs are incomplete or invalid."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def github_file_url(repository_url: str, path: str, ref: str = "main") -> str:
    """Return a browser URL for a file in a GitHub repository."""
    return f"{repository_url.rstrip('/')}/blob/{ref}/{path.lstrip('/')}"


def github_repository_url(repository: Path) -> str | None:
    """Resolve a checkout's origin to an HTTPS GitHub repository URL."""
    completed = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )
    remote = completed.stdout.strip()
    if remote.startswith("git@github.com:"):
        remote = f"https://github.com/{remote.removeprefix('git@github.com:')}"
    elif remote.startswith("ssh://git@github.com/"):
        remote = f"https://github.com/{remote.removeprefix('ssh://git@github.com/')}"
    if not remote.startswith("https://github.com/"):
        return None
    return remote.removesuffix(".git")


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise CatalogError(f"{display_path(path)} has no YAML frontmatter")

    block = text[4 : text.index("\n---\n", 4)]
    result: dict[str, str] = {}
    lines = block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value in {">", ">-", ">+", "|", "|-", "|+"}:
            style = value[0]
            continuation: list[str] = []
            index += 1
            while index < len(lines) and (
                not lines[index].strip() or lines[index].startswith((" ", "\t"))
            ):
                continuation.append(lines[index].strip())
                index += 1
            result[key.strip()] = (
                " ".join(part for part in continuation if part)
                if style == ">"
                else "\n".join(continuation).strip()
            )
            continue
        result[key.strip()] = value.strip("\"'")
        index += 1
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
    special_names = {
        "figma": "Figma",
        "github": "GitHub",
        "swiftui": "SwiftUI",
        "use": "Use",
    }
    return " ".join(
        special_names.get(part, part.upper() if len(part) <= 3 else part.title())
        for part in name.split("-")
    )


def read_skill_interface(
    skill_root: Path, frontmatter: dict[str, str]
) -> tuple[str | None, str | None, str]:
    agents_manifest = skill_root / "agents/openai.yaml"
    if not agents_manifest.exists():
        invocation = (
            "Explicit"
            if frontmatter.get("disable-model-invocation", "").lower() == "true"
            else "Automatic"
        )
        return None, None, invocation

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


def skill_item(
    skill_path: Path,
    *,
    source: str = "local",
    source_label: str = "Managed here",
    source_url: str | None = None,
) -> dict[str, Any]:
    skill_root = skill_path.parent
    frontmatter = read_frontmatter(skill_path)
    name = frontmatter.get("name")
    if not name or name != skill_root.name:
        raise CatalogError(f"{display_path(skill_path)} name must match its directory")

    display_name, short_description, invocation = read_skill_interface(skill_root, frontmatter)
    return {
        "availability": "Global",
        "description": short_description or frontmatter.get("description", ""),
        "displayName": display_name or humanize_name(name),
        "featured": SKILL_PRIORITY.get(name, 50),
        "id": f"skill:{name}",
        "invocation": invocation,
        "name": name,
        "path": skill_path.relative_to(ROOT).as_posix(),
        "runtimes": ["codex", "claude"],
        "source": source,
        "sourceLabel": source_label,
        "sourceUrl": source_url
        or github_file_url(
            AGENT_TOOLING_REPOSITORY,
            skill_path.relative_to(ROOT).as_posix(),
        ),
        "state": "Configured",
        "type": "skill",
        "version": read_skill_version(skill_path),
    }


def project_skill_items(repos_root: Path) -> list[dict[str, Any]]:
    if not repos_root.is_dir():
        raise CatalogError(f"repositories root does not exist: {repos_root}")

    items: list[dict[str, Any]] = []
    for repository in sorted(
        path for path in repos_root.iterdir() if path.is_dir() and (path / ".git").is_dir()
    ):
        if repository.resolve() == ROOT.resolve():
            continue
        skills_root = repository / ".agents/skills"
        if not skills_root.is_dir():
            continue

        locked_skills: dict[str, Any] = {}
        lock_path = repository / "skills-lock.json"
        if lock_path.is_file():
            lock_data = load_json(lock_path)
            if lock_data.get("version") == 1 and isinstance(lock_data.get("skills"), dict):
                locked_skills = lock_data["skills"]

        for skill_path in sorted(skills_root.glob("*/SKILL.md")):
            skill_root = skill_path.parent
            frontmatter = read_frontmatter(skill_path)
            name = frontmatter.get("name")
            if not name or name != skill_root.name:
                raise CatalogError(f"{display_path(skill_path)} name must match its directory")

            display_name, short_description, invocation = read_skill_interface(
                skill_root, frontmatter
            )
            lock_entry = locked_skills.get(name, {})
            upstream_source = lock_entry.get("source") if isinstance(lock_entry, dict) else None
            source = (
                "personal"
                if upstream_source == PATRICK_SKILLS_SOURCE
                else "third-party"
                if upstream_source
                else "repository"
            )
            source_label = (
                UPSTREAM_SOURCE_LABELS.get(upstream_source, upstream_source)
                if upstream_source
                else repository.name
            )
            repository_url = github_repository_url(repository)
            relative_skill_path = f".agents/skills/{name}/SKILL.md"
            source_url = None
            if upstream_source:
                source_url = github_file_url(
                    f"https://github.com/{upstream_source}",
                    lock_entry["skillPath"],
                    lock_entry.get("ref", "main"),
                )
            elif repository_url:
                source_url = github_file_url(repository_url, relative_skill_path)
            claude_skill = repository / ".claude/skills" / name / "SKILL.md"
            runtimes = ["codex"]
            if claude_skill.is_file():
                runtimes.append("claude")

            items.append(
                {
                    "availability": "Project",
                    "description": short_description or frontmatter.get("description", ""),
                    "displayName": display_name or humanize_name(name),
                    "featured": 600,
                    "id": f"project-skill:{repository.name}:{name}",
                    "invocation": invocation,
                    "name": name,
                    "path": f"{repository.name}/.agents/skills/{name}/SKILL.md",
                    "pathHref": None,
                    "repository": repository.name,
                    "runtimes": runtimes,
                    "source": source,
                    "sourceLabel": source_label,
                    "sourceUrl": source_url,
                    "state": "Installed",
                    "type": "skill",
                    "version": read_skill_version(skill_path),
                }
            )
    return items


def plugin_item(
    capability_id: str,
    installations: list[dict[str, Any]],
    metadata: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    runtime_order = {"codex": 0, "claude": 1}
    installations = sorted(
        installations,
        key=lambda item: (runtime_order.get(item["runtime"], 99), item["pluginId"]),
    )
    plugin_ids = list(dict.fromkeys(item["pluginId"] for item in installations))
    runtimes = list(dict.fromkeys(item["runtime"] for item in installations))
    name = plugin_ids[0].split("@", 1)[0]
    paths = list(dict.fromkeys(item["path"] for item in installations))
    state = (
        "Managed by Codex"
        if all(item["delivery"] == "managed" for item in installations)
        else "Configured"
    )
    return {
        "availability": "Global",
        "description": metadata["description"],
        "displayName": metadata.get("displayName", humanize_name(name)),
        "featured": 100 + index,
        "id": f"plugin:{capability_id}",
        "installations": installations,
        "invocation": None,
        "name": name,
        "path": metadata.get("path") or (paths[0] if len(paths) == 1 else None),
        "pluginIds": plugin_ids,
        "runtimes": runtimes,
        "source": metadata["source"],
        "sourceLabel": metadata["sourceLabel"],
        "sourceUrl": metadata.get("sourceUrl"),
        "state": state,
        "type": "plugin",
        "version": metadata.get("version", "Managed"),
    }


def build_catalog() -> dict[str, Any]:
    plugin_metadata = load_json(PLUGIN_METADATA)

    skill_items: list[dict[str, Any]] = []
    skills_lock = load_json(SKILLS_LOCK)
    locked_skills = skills_lock.get("skills", {})
    upstream_paths = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    upstream_names = {path.parent.name for path in upstream_paths}
    if skills_lock.get("version") != 1 or not isinstance(locked_skills, dict):
        raise CatalogError("skills-lock.json must use the official version 1 schema")
    if upstream_names != set(locked_skills):
        raise CatalogError(
            "skills-lock.json and .agents/skills disagree; "
            f"lock={sorted(locked_skills)}, files={sorted(upstream_names)}"
        )
    for path in upstream_paths:
        lock_entry = locked_skills[path.parent.name]
        source = lock_entry.get("source")
        source_label = UPSTREAM_SOURCE_LABELS.get(source)
        if not source_label:
            raise CatalogError(f"no catalog source label for locked skill source {source!r}")
        is_patrick_skill = source == PATRICK_SKILLS_SOURCE
        skill_items.append(
            skill_item(
                path,
                source="personal" if is_patrick_skill else "third-party",
                source_label=source_label,
                source_url=github_file_url(
                    f"https://github.com/{source}",
                    lock_entry["skillPath"],
                    lock_entry.get("ref", "main"),
                ),
            )
        )

    plugin_groups: dict[str, list[dict[str, Any]]] = {}
    for runtime in ("codex", "claude"):
        manifest_path = ROOT / f"config/{runtime}-plugins.txt"
        for plugin_id in read_plugin_entries(manifest_path):
            capability_id = plugin_metadata[plugin_id].get("capabilityId", plugin_id)
            plugin_groups.setdefault(capability_id, []).append(
                {
                    "delivery": "marketplace",
                    "path": manifest_path.relative_to(ROOT).as_posix(),
                    "pluginId": plugin_id,
                    "runtime": runtime,
                }
            )

    managed_codex_path = ROOT / "config/codex-managed-plugins.txt"
    managed_codex = read_plugin_entries(managed_codex_path)

    configured_ids = {
        installation["pluginId"]
        for installations in plugin_groups.values()
        for installation in installations
    } | set(managed_codex)
    metadata_ids = set(plugin_metadata)
    if configured_ids != metadata_ids:
        missing = sorted(configured_ids - metadata_ids)
        stale = sorted(metadata_ids - configured_ids)
        raise CatalogError(f"plugin metadata mismatch; missing={missing}, stale={stale}")

    for plugin_id in managed_codex:
        capability_id = plugin_metadata[plugin_id].get("capabilityId", plugin_id)
        plugin_groups.setdefault(capability_id, []).append(
            {
                "delivery": "managed",
                "path": "config/codex-managed-plugins.txt",
                "pluginId": plugin_id,
                "runtime": "codex",
            }
        )

    plugin_items = []
    for index, (capability_id, installations) in enumerate(plugin_groups.items()):
        primary_id = installations[0]["pluginId"]
        plugin_items.append(
            plugin_item(
                capability_id,
                installations,
                plugin_metadata[primary_id],
                index,
            )
        )
    items = sorted(skill_items + plugin_items, key=lambda item: (item["featured"], item["name"]))
    return {
        "generatedFrom": [
            ".agents/skills/*/SKILL.md",
            "skills-lock.json",
            "config/superpowers.json",
            "config/codex-plugins.txt",
            "config/codex-managed-plugins.txt",
            "config/claude-plugins.txt",
            "catalog/plugin-metadata.json",
        ],
        "items": items,
        "schemaVersion": 4,
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


def build_runtime_snapshot(repos_root: Path | None = None) -> dict[str, Any]:
    canonical = build_catalog()
    canonical_skills = [item for item in canonical["items"] if item["type"] == "skill"]
    plugin_metadata = load_json(PLUGIN_METADATA)
    desired_ids = {
        (installation["pluginId"], installation["runtime"]): item
        for item in canonical["items"]
        if item["type"] == "plugin"
        for installation in item["installations"]
    }
    items: list[dict[str, Any]] = []
    codex_data = run_json_command(["codex", "plugin", "list", "--json"])
    for skill in canonical_skills:
        installed_runtimes = []
        if (Path.home() / ".agents/skills" / skill["name"] / "SKILL.md").exists():
            installed_runtimes.append("codex")
        claude_config_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
        if (claude_config_dir / "skills" / skill["name"] / "SKILL.md").exists():
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
        capability_id = (
            desired["id"].removeprefix("plugin:")
            if desired
            else plugin_metadata.get(plugin_id, {}).get("capabilityId", plugin_id)
        )
        items.append(
            {
                "capabilityId": capability_id,
                "availability": "Global",
                "description": (
                    desired["description"]
                    if desired
                    else f"Installed Codex plugin from {source_label}."
                ),
                "displayName": desired["displayName"] if desired else humanize_name(plugin["name"]),
                "featured": 200 + (0 if desired else 100) + index,
                "id": f"runtime:codex:{plugin_id}",
                "installations": [
                    {
                        "delivery": (
                            "runtime"
                            if plugin_id.rsplit("@", 1)[-1]
                            in {"openai-bundled", "openai-primary-runtime"}
                            else "marketplace"
                        ),
                        "pluginId": plugin_id,
                        "runtime": "codex",
                        "state": "Enabled" if plugin.get("enabled") else "Disabled",
                        "version": plugin.get("version") or "Unknown",
                    }
                ],
                "invocation": None,
                "name": plugin["name"],
                "path": desired["path"] if desired else None,
                "pluginId": plugin_id,
                "runtimes": ["codex"],
                "source": source,
                "sourceLabel": source_label,
                "sourceUrl": desired.get("sourceUrl") if desired else None,
                "state": "Enabled" if plugin.get("enabled") else "Disabled",
                "type": "plugin",
                "version": plugin.get("version") or "Unknown",
            }
        )

    claude_data = run_json_command(["claude", "plugin", "list", "--json"])
    user_plugins = [plugin for plugin in claude_data if plugin.get("scope") == "user"]
    for index, plugin in enumerate(user_plugins):
        plugin_id = plugin["id"]
        if plugin_id.endswith("@skills-dir"):
            continue
        source, source_label = source_details(plugin_id, plugin_metadata)
        desired = desired_ids.get((plugin_id, "claude"))
        capability_id = (
            desired["id"].removeprefix("plugin:")
            if desired
            else plugin_metadata.get(plugin_id, {}).get("capabilityId", plugin_id)
        )
        items.append(
            {
                "capabilityId": capability_id,
                "availability": "Global",
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
                "installations": [
                    {
                        "delivery": "marketplace",
                        "pluginId": plugin_id,
                        "runtime": "claude",
                        "state": "Enabled" if plugin.get("enabled") else "Disabled",
                        "version": plugin.get("version") or "Unknown",
                    }
                ],
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

    items = merge_runtime_plugins(items)

    if repos_root is not None:
        items.extend(project_skill_items(repos_root))

    return {
        "generatedAt": datetime.now(UTC).isoformat(),
        "items": items,
        "message": (
            "Installed global capabilities and project skills found under the selected "
            "repositories root."
            if repos_root is not None
            else "What Codex and Claude currently report as installed on this computer."
        ),
        "schemaVersion": 4,
    }


def merge_runtime_plugins(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runtime_order = {"codex": 0, "claude": 1}
    non_plugins = [item for item in items if item["type"] != "plugin"]
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if item["type"] == "plugin":
            groups.setdefault(item["capabilityId"], []).append(item)

    merged = []
    for capability_id, group in groups.items():
        primary = next((item for item in group if item.get("path")), group[0])
        installations = [
            installation for item in group for installation in item.get("installations", [])
        ]
        installations.sort(
            key=lambda item: (runtime_order.get(item["runtime"], 99), item["pluginId"])
        )
        runtimes = list(dict.fromkeys(item["runtime"] for item in installations))
        states = {item["state"] for item in installations}
        versions = [f"{humanize_name(item['runtime'])} {item['version']}" for item in installations]
        merged_item = dict(primary)
        merged_item.update(
            {
                "id": f"runtime:capability:{capability_id}",
                "installations": installations,
                "pluginIds": list(dict.fromkeys(item["pluginId"] for item in installations)),
                "runtimes": runtimes,
                "state": states.pop() if len(states) == 1 else "Partial",
                "version": versions[0].split(" ", 1)[1]
                if len(versions) == 1
                else " · ".join(versions),
            }
        )
        merged_item.pop("capabilityId", None)
        merged_item.pop("pluginId", None)
        merged.append(merged_item)

    return non_plugins + merged


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
    parser.add_argument(
        "--repos-root",
        type=Path,
        help="Include project skills from immediate child repositories in the local snapshot.",
    )
    args = parser.parse_args()

    if args.repos_root is not None and not args.snapshot_runtime:
        parser.error("--repos-root requires --snapshot-runtime")

    try:
        write_or_check_catalog(check=args.check)
        if args.snapshot_runtime:
            RUNTIME_DATA.write_text(
                rendered_json(build_runtime_snapshot(args.repos_root)), encoding="utf-8"
            )
            print(f"Generated local snapshot {RUNTIME_DATA.relative_to(ROOT)}.")
            print("Open /catalog/?runtime=local and choose This Mac to view it.")
    except (CatalogError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Catalog generation failed: {error}") from error


if __name__ == "__main__":
    main()
