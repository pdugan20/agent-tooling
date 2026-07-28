#!/usr/bin/env python3

"""Validate canonical skills, plugin dependencies, and release invariants."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPERPOWERS_CONFIG = ROOT / "config/superpowers.json"
ROOT_PACKAGE = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
RELEASE_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
CUSTOM_SKILLS = {
    "feature-delivery": True,
    "production-hardening": False,
}
EXPECTED_EXPLICIT_SUPERPOWERS = {
    "brainstorming",
    "dispatching-parallel-agents",
    "executing-plans",
    "finishing-a-development-branch",
    "subagent-driven-development",
    "test-driven-development",
    "using-git-worktrees",
    "using-superpowers",
    "writing-plans",
}
EXPECTED_AUTOMATIC_SUPERPOWERS = {
    "receiving-code-review",
    "requesting-code-review",
    "systematic-debugging",
    "verification-before-completion",
    "writing-skills",
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
    package_version = repository_version()
    package_lock = load_json(PACKAGE_LOCK)
    if package_lock.get("version") != package_version:
        raise ValidationError("package-lock root version must match package.json")
    lock_package = package_lock.get("packages", {}).get("", {})
    if lock_package.get("version") != package_version:
        raise ValidationError("package-lock packages root version must match package.json")

    superpowers = load_json(SUPERPOWERS_CONFIG)
    if superpowers.get("upstreamRepository") != "https://github.com/obra/superpowers.git":
        raise ValidationError("Superpowers upstream repository must remain obra/superpowers")
    if superpowers.get("forkRepository") != "https://github.com/pdugan20/superpowers.git":
        raise ValidationError("Superpowers fork repository must remain pdugan20/superpowers")
    if superpowers.get("marketplace") != "superpowers-configured":
        raise ValidationError("Superpowers marketplace must remain superpowers-configured")
    if superpowers.get("pluginId") != "superpowers@superpowers-configured":
        raise ValidationError("Superpowers plugin ID must match its configured marketplace")

    upstream_version = superpowers.get("upstreamVersion")
    fork_version = superpowers.get("forkVersion")
    if not isinstance(upstream_version, str) or not SEMVER_RE.fullmatch(upstream_version):
        raise ValidationError("Superpowers upstreamVersion must be valid SemVer")
    if not isinstance(fork_version, str) or not re.fullmatch(
        rf"{re.escape(upstream_version)}-config\.[1-9]\d*", fork_version
    ):
        raise ValidationError("Superpowers forkVersion must extend upstreamVersion with -config.N")
    if not re.fullmatch(r"[0-9a-f]{40}", str(superpowers.get("upstreamCommit", ""))):
        raise ValidationError("Superpowers upstreamCommit must be a full Git SHA")
    if set(superpowers.get("explicitOnlySkills", [])) != EXPECTED_EXPLICIT_SUPERPOWERS:
        raise ValidationError("Superpowers explicit-only skill inventory changed unexpectedly")
    if set(superpowers.get("automaticSkills", [])) != EXPECTED_AUTOMATIC_SUPERPOWERS:
        raise ValidationError("Superpowers automatic skill inventory changed unexpectedly")
    patches = superpowers.get("patches")
    if (
        not isinstance(patches, list)
        or not patches
        or not all(isinstance(item, str) and item for item in patches)
    ):
        raise ValidationError("Superpowers patches must be a non-empty string list")

    retired_plugin_root = ROOT / "plugins/patrick-delivery"
    if any(path.is_file() or path.is_symlink() for path in retired_plugin_root.rglob("*")):
        raise ValidationError("retired Patrick Delivery plugin must not remain in the repository")
    if (ROOT / ".agents/plugins/marketplace.json").exists():
        raise ValidationError(
            "retired personal plugin marketplace must not remain in the repository"
        )

    for skill_name, expected_implicit in CUSTOM_SKILLS.items():
        skill_root = ROOT / "skills" / skill_name
        frontmatter = read_frontmatter(skill_root / "SKILL.md")
        if frontmatter.get("name") != skill_name:
            raise ValidationError(f"{skill_name} frontmatter name must match its directory")
        actual_implicit = read_implicit_invocation(skill_root / "agents/openai.yaml")
        if actual_implicit is not expected_implicit:
            raise ValidationError(
                f"{skill_name} allow_implicit_invocation must be {str(expected_implicit).lower()}"
            )

    plugin_manifests: dict[str, list[str]] = {}
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
        plugin_manifests[manifest_path.name] = entries

    plugin_id = str(superpowers["pluginId"])
    if plugin_id not in plugin_manifests["codex-plugins.txt"]:
        raise ValidationError("configured Superpowers must be desired in Codex")
    if plugin_id not in plugin_manifests["claude-plugins.txt"]:
        raise ValidationError("configured Superpowers must be desired in Claude")
    retired_ids = {"patrick-delivery@personal", "superpowers@claude-plugins-official"}
    if any(retired_ids & set(entries) for entries in plugin_manifests.values()):
        raise ValidationError("retired delivery or official Superpowers plugins remain desired")

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
