#!/usr/bin/env python3

"""Validate the canonical plugin, skill, and release invariants."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins/patrick-delivery"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin/plugin.json"
MARKETPLACE_MANIFEST = ROOT / ".agents/plugins/marketplace.json"
ROOT_PACKAGE = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
RELEASE_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
DELIVERY_SKILLS = {
    "execute-plan": False,
    "feature-delivery": True,
    "formal-spec": False,
    "production-hardening": False,
    "strict-tdd": False,
    "write-plan": False,
}


class ValidationError(Exception):
    """Raised when a repository invariant is violated."""


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValidationError(f"{path.relative_to(ROOT)} has no YAML frontmatter")

    frontmatter = text[4 : text.index("\n---\n", 4)]
    result: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def read_implicit_invocation(path: Path) -> bool:
    match = re.search(
        r"(?m)^\s*allow_implicit_invocation:\s*(true|false)\s*$",
        path.read_text(encoding="utf-8"),
    )
    if not match:
        raise ValidationError(f"{path.relative_to(ROOT)} lacks allow_implicit_invocation")
    return match.group(1) == "true"


def plugin_version() -> str:
    version = load_json(PLUGIN_MANIFEST).get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise ValidationError("Patrick Delivery manifest version must be valid SemVer")
    return version


def repository_version() -> str:
    version = load_json(ROOT_PACKAGE).get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise ValidationError("root package version must be valid SemVer")
    return version


def validate_release_tag(tag: str) -> str:
    match = RELEASE_TAG_RE.fullmatch(tag)
    if not match:
        raise ValidationError("release tag must use vMAJOR.MINOR.PATCH")
    version = match.group("version")
    package_version = repository_version()
    if version != package_version:
        raise ValidationError(
            f"release tag version {version} does not match root package version {package_version}"
        )
    if not re.search(rf"(?m)^## \[{re.escape(version)}\](?:\s+-|\s*$)", CHANGELOG.read_text()):
        raise ValidationError(f"CHANGELOG.md has no [{version}] release section")
    return version


def validate_repository() -> None:
    manifest = load_json(PLUGIN_MANIFEST)
    if manifest.get("name") != "patrick-delivery":
        raise ValidationError("Patrick Delivery manifest name changed unexpectedly")
    if manifest.get("skills") != "./skills/":
        raise ValidationError("Patrick Delivery manifest must load ./skills/")
    plugin_version()
    package_version = repository_version()
    package_lock = load_json(PACKAGE_LOCK)
    if package_lock.get("version") != package_version:
        raise ValidationError("package-lock root version must match package.json")
    lock_package = package_lock.get("packages", {}).get("", {})
    if lock_package.get("version") != package_version:
        raise ValidationError("package-lock packages root version must match package.json")

    marketplace = load_json(MARKETPLACE_MANIFEST)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise ValidationError("personal marketplace plugins must be a list")
    matches = [plugin for plugin in plugins if plugin.get("name") == "patrick-delivery"]
    if len(matches) != 1:
        raise ValidationError("personal marketplace must contain Patrick Delivery exactly once")
    source = matches[0].get("source")
    if source != {"source": "local", "path": "./plugins/patrick-delivery"}:
        raise ValidationError("Patrick Delivery marketplace source must remain canonical and local")

    actual_skills = {path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")}
    if actual_skills != DELIVERY_SKILLS.keys():
        raise ValidationError(
            "Patrick Delivery skill set mismatch: "
            f"expected {sorted(DELIVERY_SKILLS)}, got {sorted(actual_skills)}"
        )

    for skill_name, expected_implicit in DELIVERY_SKILLS.items():
        skill_root = PLUGIN_ROOT / "skills" / skill_name
        frontmatter = read_frontmatter(skill_root / "SKILL.md")
        if frontmatter.get("name") != skill_name:
            raise ValidationError(f"{skill_name} frontmatter name must match its directory")
        actual_implicit = read_implicit_invocation(skill_root / "agents/openai.yaml")
        if actual_implicit is not expected_implicit:
            raise ValidationError(
                f"{skill_name} allow_implicit_invocation must be {str(expected_implicit).lower()}"
            )

    for manifest_path in (ROOT / "config/codex-plugins.txt", ROOT / "config/claude-plugins.txt"):
        entries = [
            line.strip()
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if len(entries) != len(set(entries)):
            raise ValidationError(f"{manifest_path.relative_to(ROOT)} contains duplicates")
        invalid = [entry for entry in entries if not re.fullmatch(r"[^@\s]+@[^@\s]+", entry)]
        if invalid:
            raise ValidationError(
                f"{manifest_path.relative_to(ROOT)} has invalid plugin IDs: {invalid}"
            )

    for workflow_path in (
        ROOT / ".github/workflows/ci.yml",
        ROOT / ".github/workflows/release.yml",
    ):
        workflow = workflow_path.read_text(encoding="utf-8")
        if "fetch-depth: 0" not in workflow:
            raise ValidationError(
                f"{workflow_path.relative_to(ROOT)} must fetch full history for Gitleaks"
            )

    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    required_gitleaks_hooks = (
        "gitleaks git --pre-commit --staged",
        "gitleaks git --redact --no-banner --verbose .",
    )
    if not all(command in pre_commit for command in required_gitleaks_hooks):
        raise ValidationError("pre-commit must scan staged changes and full history")

    verification = (ROOT / "scripts/verify-repo.sh").read_text(encoding="utf-8")
    if "gitleaks git --redact --no-banner --verbose ." not in verification:
        raise ValidationError("repository verification must scan full Git history")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-tag")
    args = parser.parse_args()

    try:
        validate_repository()
        if args.release_tag:
            version = validate_release_tag(args.release_tag)
            print(f"Agent tooling release tag matches repository version {version}.")
        else:
            print("Agent tooling repository policy verified.")
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        raise SystemExit(f"Repository policy validation failed: {error}") from error


if __name__ == "__main__":
    main()
