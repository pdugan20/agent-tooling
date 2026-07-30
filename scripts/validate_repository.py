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
    "code-native-ui-ideation": True,
    "feature-delivery": True,
    "production-hardening": False,
}
UPSTREAM_SKILLS = {
    "code-native-ui-ideation": (
        "pdugan20/patrick-workflows",
        "skills/code-native-ui-ideation/SKILL.md",
    ),
    "feature-delivery": (
        "pdugan20/patrick-workflows",
        "skills/feature-delivery/SKILL.md",
    ),
    "production-hardening": (
        "pdugan20/patrick-workflows",
        "skills/production-hardening/SKILL.md",
    ),
    "animation-vocabulary": ("emilkowalski/skills", "skills/animation-vocabulary/SKILL.md"),
    "apple-design": ("emilkowalski/skills", "skills/apple-design/SKILL.md"),
    "emil-design-eng": ("emilkowalski/skills", "skills/emil-design-eng/SKILL.md"),
    "find-animation-opportunities": (
        "emilkowalski/skills",
        "skills/find-animation-opportunities/SKILL.md",
    ),
    "pick-ui-library": ("emilkowalski/skills", "skills/pick-ui-library/SKILL.md"),
    "review-animations": ("emilkowalski/skills", "skills/review-animations/SKILL.md"),
    "swiftui-pro": ("twostraws/swiftui-agent-skill", "swiftui-pro/SKILL.md"),
}
PATRICK_WORKFLOWS_REF = "v1.0.0"
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

    legacy_skills_root = ROOT / "skills"
    if legacy_skills_root.exists() and any(legacy_skills_root.glob("*/SKILL.md")):
        raise ValidationError("skills/ must not duplicate CLI-managed skill snapshots")

    for skill_name, expected_implicit in CUSTOM_SKILLS.items():
        skill_root = ROOT / ".agents/skills" / skill_name
        frontmatter = read_frontmatter(skill_root / "SKILL.md")
        if frontmatter.get("name") != skill_name:
            raise ValidationError(f"{skill_name} frontmatter name must match its directory")
        actual_implicit = read_implicit_invocation(skill_root / "agents/openai.yaml")
        if actual_implicit is not expected_implicit:
            raise ValidationError(
                f"{skill_name} allow_implicit_invocation must be {str(expected_implicit).lower()}"
            )

    skills_lock = load_json(ROOT / "skills-lock.json")
    locked_skills = skills_lock.get("skills")
    if skills_lock.get("version") != 1 or not isinstance(locked_skills, dict):
        raise ValidationError("skills-lock.json must use the official version 1 schema")
    if set(locked_skills) != set(UPSTREAM_SKILLS):
        raise ValidationError("skills-lock.json must contain the exact upstream skill set")
    upstream_skill_names = {
        path.name for path in (ROOT / ".agents/skills").iterdir() if (path / "SKILL.md").is_file()
    }
    if upstream_skill_names != set(UPSTREAM_SKILLS):
        raise ValidationError(".agents/skills must match the exact locked upstream skill set")
    nested_skill_files = set((ROOT / ".agents/skills").glob("*/skills/*/SKILL.md"))
    expected_nested_skill = ROOT / ".agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"
    if nested_skill_files != {expected_nested_skill}:
        raise ValidationError("the SwiftUI upstream compatibility skill changed unexpectedly")
    for skill_name, (expected_source, expected_path) in UPSTREAM_SKILLS.items():
        lock_entry = locked_skills[skill_name]
        if not isinstance(lock_entry, dict):
            raise ValidationError(f"locked skill {skill_name} must be an object")
        if lock_entry.get("source") != expected_source:
            raise ValidationError(f"locked skill {skill_name} has an unexpected source")
        if lock_entry.get("skillPath") != expected_path:
            raise ValidationError(f"locked skill {skill_name} has an unexpected source path")
        if (
            expected_source == "pdugan20/patrick-workflows"
            and lock_entry.get("ref") != PATRICK_WORKFLOWS_REF
        ):
            raise ValidationError(
                f"locked skill {skill_name} must pin Patrick Workflows {PATRICK_WORKFLOWS_REF}"
            )
        if lock_entry.get("sourceType") != "github" or not re.fullmatch(
            r"[0-9a-f]{64}", str(lock_entry.get("computedHash", ""))
        ):
            raise ValidationError(f"locked skill {skill_name} lacks official CLI provenance")
        claude_link = ROOT / ".claude/skills" / skill_name
        expected_target = Path("../../.agents/skills") / skill_name
        if not claude_link.is_symlink() or claude_link.readlink() != expected_target:
            raise ValidationError(
                f".claude/skills/{skill_name} must link to {expected_target.as_posix()}"
            )

    plugin_manifests: dict[str, list[str]] = {}
    for manifest_path in (
        ROOT / "config/codex-plugins.txt",
        ROOT / "config/codex-managed-plugins.txt",
        ROOT / "config/claude-plugins.txt",
    ):
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
    mintlify_docs_id = "mintlify-docs@patrick-tools"
    if not all(
        mintlify_docs_id in plugin_manifests[name]
        for name in ("codex-plugins.txt", "claude-plugins.txt")
    ):
        raise ValidationError("mintlify-docs must be desired in both Codex and Claude")
    expo_id = "expo@claude-plugins-official"
    if expo_id not in plugin_manifests["codex-plugins.txt"]:
        raise ValidationError("the current vendor-backed Expo plugin must be desired in Codex")
    if expo_id not in plugin_manifests["claude-plugins.txt"]:
        raise ValidationError("the current vendor-backed Expo plugin must be desired in Claude")
    required_direct_codex_plugins = {
        "mintlify@mintlify-marketplace",
        "sentry@claude-plugins-official",
    }
    if not required_direct_codex_plugins <= set(plugin_manifests["codex-plugins.txt"]):
        raise ValidationError("vendor-backed Mintlify and Sentry plugins must be desired in Codex")
    required_managed_codex_plugins = {
        "figma@openai-curated-remote",
        "github@openai-curated-remote",
        "vercel@openai-curated-remote",
    }
    if not required_managed_codex_plugins <= set(plugin_manifests["codex-managed-plugins.txt"]):
        raise ValidationError("Figma, GitHub, and Vercel must remain Codex-managed")
    required_claude_plugins = {
        "cloudflare@claude-plugins-official",
        "figma@claude-plugins-official",
        "firebase@claude-plugins-official",
        "github@claude-plugins-official",
        "mintlify@mintlify-marketplace",
        "plugin-dev@claude-plugins-official",
        "sentry@claude-plugins-official",
        "supabase@claude-plugins-official",
        "vercel@claude-plugins-official",
    }
    if not required_claude_plugins <= set(plugin_manifests["claude-plugins.txt"]):
        raise ValidationError("the canonical Claude capability set is incomplete")
    if set(plugin_manifests["codex-plugins.txt"]) & set(
        plugin_manifests["codex-managed-plugins.txt"]
    ):
        raise ValidationError("Codex-managed plugins cannot also be CLI-managed")
    retired_ids = {
        "patrick-delivery@personal",
        "mintlify-docs@pdugan20-plugins",
        "superpowers@claude-plugins-official",
        "expo@openai-curated",
        "sentry@openai-curated",
        "mintlify@claude-plugins-official",
        "playwright@claude-plugins-official",
        "figma@openai-curated",
        "github@openai-curated",
        "vercel@openai-curated",
    }
    if any(retired_ids & set(entries) for entries in plugin_manifests.values()):
        raise ValidationError("retired or superseded plugins remain desired")
    if "railway@claude-plugins-official" in plugin_manifests["claude-plugins.txt"]:
        raise ValidationError(
            "Railway uses a shared project skill in rss-feed-generator "
            "and must not be globally desired"
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
    required_quality_hooks = (
        "entry: typos",
        "entry: zizmor --pedantic --min-severity medium --min-confidence medium "
        "--no-online-audits .",
    )
    if not all(command in pre_commit for command in required_quality_hooks):
        raise ValidationError("pre-commit must run spelling and workflow security checks")

    verification = (ROOT / "scripts/verify-repo.sh").read_text(encoding="utf-8")
    if "gitleaks git --redact --no-banner --verbose ." not in verification:
        raise ValidationError("repository verification must scan full Git history")
    if "pre-commit actionlint gitleaks typos zizmor" not in verification:
        raise ValidationError("repository verification must require all standalone quality tools")

    ci_tools = (ROOT / "scripts/install-ci-tools.sh").read_text(encoding="utf-8")
    required_ci_tools = ("actionlint", "gitleaks", "typos", "zizmor")
    if not all(
        f"install_archive \\\n  {tool_name} \\" in ci_tools for tool_name in required_ci_tools
    ):
        raise ValidationError("CI tool installer must provision the full quality toolchain")

    for script_name in (
        "bootstrap.sh",
        "install-claude-plugins.sh",
        "refresh-claude-plugins.sh",
        "verify-setup.sh",
    ):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
        if 'claude_config_dir=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}' not in script:
            raise ValidationError(f"{script_name} must resolve the active Claude config directory")
        if '"$HOME/.claude/' in script:
            raise ValidationError(f"{script_name} must not bypass CLAUDE_CONFIG_DIR")

    for script_name in ("install-claude-plugins.sh", "refresh-claude-plugins.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
        if "scripts/reconcile_claude_plugins.py" not in script:
            raise ValidationError(
                f"{script_name} must disable undeclared enabled user-scoped plugins"
            )
        if "ensure_marketplace mintlify-marketplace mintlify/mintlify-claude-plugin" not in script:
            raise ValidationError(f"{script_name} must add Mintlify's canonical marketplace")
        if "ensure_marketplace patrick-tools pdugan20/patrick-tools" not in script:
            raise ValidationError(f"{script_name} must add Patrick's renamed marketplace")

    for script_name in ("install-codex-plugins.sh", "refresh-codex-plugins.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
        if (
            "ensure_marketplace patrick-tools https://github.com/pdugan20/patrick-tools.git"
            not in script
        ):
            raise ValidationError(f"{script_name} must add Patrick's renamed marketplace")


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
