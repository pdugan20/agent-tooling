#!/usr/bin/env python3

"""Validate canonical skills, plugin dependencies, and release invariants."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPERPOWERS_CONFIG = ROOT / "config/superpowers.json"
ROOT_PACKAGE = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"
CHANGELOG = ROOT / "CHANGELOG.md"
RENOVATE_CONFIG = ROOT / "renovate.json"
DEPENDABOT_CONFIG = ROOT / ".github/dependabot.yml"
WORKFLOWS_ROOT = ROOT / ".github/workflows"
ACTIONS_ROOT = ROOT / ".github/actions"
WORKFLOW_TEMPLATE_ROOTS = (ROOT / "workflow-templates", ROOT / ".github/workflow-templates")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
RELEASE_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
EXPECTED_RENOVATE_TOP_LEVEL = {
    "$schema": "https://docs.renovatebot.com/renovate-schema.json",
    "enabled": True,
    "extends": ["config:recommended"],
    "enabledManagers": ["npm", "github-actions"],
    "semanticCommits": "enabled",
    "semanticCommitType": "chore",
    "semanticCommitScope": "deps",
    "timezone": "America/Los_Angeles",
    "dependencyDashboard": True,
    "dependencyDashboardAutoclose": True,
    "labels": ["dependencies"],
    "branchConcurrentLimit": 3,
    "prConcurrentLimit": 3,
    "prHourlyLimit": 2,
    "rebaseWhen": "behind-base-branch",
    "platformAutomerge": True,
    "automergeType": "pr",
    "automergeStrategy": "squash",
    "internalChecksFilter": "strict",
    "vulnerabilityAlerts": {"enabled": False},
}
EXPECTED_LOCKFILE_MAINTENANCE = {
    "enabled": True,
    "schedule": ["before 6am on monday"],
    "dependencyDashboardApproval": True,
    "automerge": False,
}
EXPECTED_RENOVATE_RULES = [
    {
        "description": "Default every enabled manager to dashboard approval",
        "matchManagers": ["npm", "github-actions"],
        "dependencyDashboardApproval": True,
        "automerge": False,
    },
    {
        "description": "Stable npm development patch and minor updates",
        "matchManagers": ["npm"],
        "matchDepTypes": ["devDependencies"],
        "matchCurrentVersion": "/^[1-9]\\d*\\.\\d+\\.\\d+$/",
        "matchUpdateTypes": ["patch", "minor"],
        "groupName": "development dependencies",
        "minimumReleaseAge": "7 days",
        "dependencyDashboardApproval": False,
        "automerge": True,
    },
    {
        "description": "Pre-1.0 npm development patch updates",
        "matchManagers": ["npm"],
        "matchDepTypes": ["devDependencies"],
        "matchCurrentVersion": "/^0\\.\\d+\\.\\d+$/",
        "matchUpdateTypes": ["patch"],
        "groupName": "pre-1.0 development dependencies",
        "minimumReleaseAge": "7 days",
        "dependencyDashboardApproval": False,
        "automerge": True,
    },
    {
        "description": "Stable GitHub Actions patch and minor updates",
        "matchManagers": ["github-actions"],
        "matchCurrentVersion": "/^v?[1-9]\\d*\\.\\d+\\.\\d+$/",
        "matchUpdateTypes": ["patch", "minor"],
        "groupName": "github actions",
        "minimumReleaseAge": "14 days",
        "dependencyDashboardApproval": False,
        "automerge": True,
    },
    {
        "description": "Pre-1.0 minor updates require exception handling",
        "matchCurrentVersion": "/^0\\./",
        "matchUpdateTypes": ["minor", "major"],
        "dependencyDashboardApproval": True,
        "automerge": False,
    },
    {
        "description": "All major updates require exception handling",
        "matchUpdateTypes": ["major"],
        "dependencyDashboardApproval": True,
        "automerge": False,
    },
    {
        "description": "Unsafe update types require manual approval",
        "matchUpdateTypes": ["digest", "pin", "pinDigest", "lockFileMaintenance"],
        "dependencyDashboardApproval": True,
        "automerge": False,
    },
]
CUSTOM_SKILLS = {
    "align-ui-to-design-system": True,
    "analyze-ui-video": True,
    "audit-design-system-health": True,
    "bootstrap-repository": True,
    "code-native-ui-ideation": True,
    "feature-delivery": True,
    "feature-spike": True,
    "generate-mintlify-reference": True,
    "integrate-app-intents": True,
    "review-mintlify-docs": True,
    "scaffold-mintlify-site": True,
    "tune-mobile-client-performance": True,
    "write-mintlify-changelog": True,
}
UPSTREAM_SKILLS = {
    "align-ui-to-design-system": (
        "pdugan20/skills",
        "skills/align-ui-to-design-system/SKILL.md",
    ),
    "analyze-ui-video": (
        "pdugan20/skills",
        "skills/analyze-ui-video/SKILL.md",
    ),
    "audit-design-system-health": (
        "pdugan20/skills",
        "skills/audit-design-system-health/SKILL.md",
    ),
    "bootstrap-repository": (
        "pdugan20/skills",
        "skills/bootstrap-repository/SKILL.md",
    ),
    "code-native-ui-ideation": (
        "pdugan20/skills",
        "skills/code-native-ui-ideation/SKILL.md",
    ),
    "feature-delivery": (
        "pdugan20/skills",
        "skills/feature-delivery/SKILL.md",
    ),
    "feature-spike": (
        "pdugan20/skills",
        "skills/feature-spike/SKILL.md",
    ),
    "generate-mintlify-reference": (
        "pdugan20/skills",
        "skills/generate-mintlify-reference/SKILL.md",
    ),
    "integrate-app-intents": (
        "pdugan20/skills",
        "skills/integrate-app-intents/SKILL.md",
    ),
    "review-mintlify-docs": (
        "pdugan20/skills",
        "skills/review-mintlify-docs/SKILL.md",
    ),
    "scaffold-mintlify-site": (
        "pdugan20/skills",
        "skills/scaffold-mintlify-site/SKILL.md",
    ),
    "tune-mobile-client-performance": (
        "pdugan20/skills",
        "skills/tune-mobile-client-performance/SKILL.md",
    ),
    "write-mintlify-changelog": (
        "pdugan20/skills",
        "skills/write-mintlify-changelog/SKILL.md",
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
    "xcodebuildmcp": (
        "getsentry/XcodeBuildMCP",
        "skills/xcodebuildmcp/SKILL.md",
    ),
}
PATRICK_SKILLS_REF = "v3.2.0"
XCODEBUILDMCP_REF = "v2.7.0"
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


def load_yaml_document(source: str) -> tuple[object, list[dict[str, object]], bool]:
    script = """
const fs = require("node:fs");
const { isAlias, isMap, isScalar, isSeq, parseDocument } = require("yaml");
const source = fs.readFileSync(0, "utf8");
const usesEntries = [];
let hasAlias = false;

function lineAt(offset) {
  return source.slice(0, offset).split("\\n").length;
}

function walk(node) {
  if (isAlias(node)) {
    hasAlias = true;
    return;
  }
  if (isMap(node)) {
    for (const pair of node.items) {
      if (isScalar(pair.key) && pair.key.value === "uses") {
        const pairToken = pair.srcToken || {};
        const keyToken = pair.key.srcToken || {};
        const valueToken = pair.value && pair.value.srcToken ? pair.value.srcToken : {};
        const separators = Array.isArray(pairToken.sep) ? pairToken.sep : [];
        const endTokens = Array.isArray(valueToken.end) ? valueToken.end : [];
        const newlineIndex = endTokens.findIndex((token) => token.type === "newline");
        const commentTokens = endTokens.filter(
          (token, index) => token.type === "comment" && (newlineIndex < 0 || index < newlineIndex),
        );
        const startTokens = Array.isArray(pairToken.start) ? pairToken.start : [];
        const canonicalSyntax =
          !node.flow &&
          pairToken.explicitKey !== true &&
          startTokens.every((token) => token.type === "space") &&
          keyToken.type === "scalar" &&
          keyToken.source === "uses" &&
          pair.key.tag == null &&
          pair.key.anchor == null &&
          separators.length >= 1 &&
          separators[0].type === "map-value-ind" &&
          separators.slice(1).every((token) => token.type === "space") &&
          isScalar(pair.value) &&
          pair.value.type === "PLAIN" &&
          pair.value.tag == null &&
          pair.value.anchor == null &&
          valueToken.type === "scalar";
        usesEntries.push({
          line: lineAt(pair.key.range[0]),
          value: isScalar(pair.value) ? pair.value.value : null,
          canonicalSyntax,
          comment: commentTokens.length === 1 ? commentTokens[0].source : null,
        });
      }
      walk(pair.key);
      walk(pair.value);
    }
  } else if (isSeq(node)) {
    for (const item of node.items) walk(item);
  }
}

try {
  const document = parseDocument(source, {
    keepSourceTokens: true,
    strict: true,
    uniqueKeys: true,
  });
  const problems = [...document.errors, ...document.warnings];
  if (problems.length > 0) throw problems[0];
  walk(document.contents);
  const value = document.toJS({ maxAliasCount: 100 });
  process.stdout.write(JSON.stringify({ value, usesEntries, hasAlias }));
} catch (error) {
  process.stderr.write(String(error.message || error));
  process.exit(1);
}
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        input=source,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValidationError(f"invalid or duplicate-key YAML: {result.stderr.strip()}")
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValidationError("YAML must contain one serializable document") from error
    value = document.get("value") if isinstance(document, dict) else None
    uses_entries = document.get("usesEntries") if isinstance(document, dict) else None
    has_alias = document.get("hasAlias") if isinstance(document, dict) else None
    if not isinstance(uses_entries, list) or not all(
        isinstance(entry, dict) for entry in uses_entries
    ):
        raise ValidationError("YAML parser did not return action provenance")
    if not isinstance(has_alias, bool):
        raise ValidationError("YAML parser did not return alias provenance")
    return value, uses_entries, has_alias


def load_yaml(source: str) -> object:
    value, _, _ = load_yaml_document(source)
    return value


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


def validate_dependency_automation_policy(
    renovate: dict[str, object] | None = None,
    dependabot_source: str | None = None,
) -> None:
    renovate = load_json(RENOVATE_CONFIG) if renovate is None else renovate
    expected_keys = set(EXPECTED_RENOVATE_TOP_LEVEL) | {
        "lockFileMaintenance",
        "packageRules",
    }
    if set(renovate) != expected_keys:
        raise ValidationError("Renovate active policy has unexpected or missing top-level keys")
    for key, expected in EXPECTED_RENOVATE_TOP_LEVEL.items():
        if renovate.get(key) != expected:
            raise ValidationError(f"Renovate active policy has unsafe {key}")
    if renovate.get("lockFileMaintenance") != EXPECTED_LOCKFILE_MAINTENANCE:
        raise ValidationError("Renovate lockfile maintenance must remain approval-gated")
    if renovate.get("packageRules") != EXPECTED_RENOVATE_RULES:
        raise ValidationError("Renovate package rules drifted from the proven ownership policy")

    source = (
        DEPENDABOT_CONFIG.read_text(encoding="utf-8")
        if dependabot_source is None
        else dependabot_source
    )
    dependabot = load_yaml(source)
    if not isinstance(dependabot, dict) or set(dependabot) != {"version", "updates"}:
        raise ValidationError("Dependabot must retain only version and updates at the root")
    if dependabot.get("version") != 2:
        raise ValidationError("Dependabot must retain schema version 2")
    updates = dependabot.get("updates")
    if not isinstance(updates, list) or not all(isinstance(update, dict) for update in updates):
        raise ValidationError("Dependabot updates must be a list of mappings")
    expected_ecosystems = ["npm", "github-actions"]
    actual_ecosystems = [update.get("package-ecosystem") for update in updates]
    if actual_ecosystems != expected_ecosystems:
        raise ValidationError("Dependabot must retain exactly npm and GitHub Actions coverage")
    for update, ecosystem in zip(updates, expected_ecosystems, strict=True):
        if "ignore" in update:
            raise ValidationError(f"Dependabot {ecosystem} security updates must not be ignored")
        if update.get("directory") != "/":
            raise ValidationError(f"Dependabot {ecosystem} coverage must remain at the root")
        if update.get("target-branch") != "main":
            raise ValidationError(f"Dependabot {ecosystem} must target main")
        if update.get("open-pull-requests-limit") != 0:
            raise ValidationError(
                f"Dependabot {ecosystem} routine PRs must remain disabled during Renovate ownership"
            )


def action_reference_errors(workflow_sources: dict[str, str]) -> tuple[list[str], list[str]]:
    references: list[str] = []
    errors: list[str] = []
    pinned_action = re.compile(
        r"^(?P<action>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
        r"(?:/[A-Za-z0-9_.-]+)*)@(?P<sha>[0-9a-f]{40})$"
    )
    for workflow_path, source in workflow_sources.items():
        _, uses_entries, has_alias = load_yaml_document(source)
        if has_alias:
            errors.append(f"{workflow_path}: YAML aliases are not allowed in action metadata")
        for entry in uses_entries:
            line_number = entry.get("line")
            reference = entry.get("value")
            comment = entry.get("comment")
            if not isinstance(line_number, int) or not isinstance(reference, str):
                errors.append(f"{workflow_path}: uses must resolve to a string")
                continue
            references.append(f"{reference} {comment}" if isinstance(comment, str) else reference)
            if entry.get("canonicalSyntax") is not True:
                errors.append(
                    f"{workflow_path}:{line_number}: uses must use canonical block-key syntax"
                )
            if reference.startswith("./"):
                continue
            if not pinned_action.fullmatch(reference) or not (
                isinstance(comment, str) and re.fullmatch(r"# v\d+\.\d+\.\d+", comment)
            ):
                errors.append(
                    f"{workflow_path}:{line_number}: external action must use a full SHA "
                    "and exact vMAJOR.MINOR.PATCH comment"
                )
    return references, errors


def github_action_sources() -> dict[str, str]:
    paths = [
        path
        for path in WORKFLOWS_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".yml", ".yaml"}
    ]
    if ACTIONS_ROOT.exists():
        paths.extend(
            path
            for path in ACTIONS_ROOT.rglob("*")
            if path.is_file() and path.name in {"action.yml", "action.yaml"}
        )
    for template_root in WORKFLOW_TEMPLATE_ROOTS:
        if template_root.exists():
            paths.extend(
                path
                for path in template_root.rglob("*")
                if path.is_file() and path.suffix in {".yml", ".yaml"}
            )
    paths.extend(path for path in (ROOT / "action.yml", ROOT / "action.yaml") if path.is_file())
    return {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(paths)
    }


def validate_workflow_automation_safety(workflow_sources: dict[str, str] | None = None) -> None:
    sources = github_action_sources() if workflow_sources is None else workflow_sources
    references, errors = action_reference_errors(sources)
    if not references:
        raise ValidationError("repository workflows must execute at least one action")
    if errors:
        raise ValidationError("\n".join(errors))

    ci = load_yaml(sources.get(".github/workflows/ci.yml", ""))
    release = load_yaml(sources.get(".github/workflows/release.yml", ""))
    if not isinstance(ci, dict) or ci.get("on") != {
        "pull_request": None,
        "push": {"branches": ["main"]},
    }:
        raise ValidationError("CI must remain limited to pull requests and main pushes")
    if not isinstance(release, dict) or release.get("on") != {"push": {"tags": ["v*"]}}:
        raise ValidationError("release workflow must remain tag-only")
    release_jobs = release.get("jobs")
    release_job = release_jobs.get("release") if isinstance(release_jobs, dict) else None
    release_steps = release_job.get("steps") if isinstance(release_job, dict) else None
    if not isinstance(release_steps, list):
        raise ValidationError("release workflow must retain its release job")
    release_runs = [step.get("run") for step in release_steps if isinstance(step, dict)]
    install_command = "npm ci"
    tag_command = 'python scripts/validate_repository.py --release-tag "$GITHUB_REF_NAME"'
    if (
        release_runs.count(install_command) != 1
        or release_runs.count(tag_command) != 1
        or release_runs.index(install_command) > release_runs.index(tag_command)
    ):
        raise ValidationError("release workflow must install npm dependencies before validation")
    if ci.get("permissions") != {"contents": "read"}:
        raise ValidationError("pull-request CI must retain read-only permissions")
    jobs = ci.get("jobs")
    if not isinstance(jobs, dict) or set(jobs) != {"ci"}:
        raise ValidationError("required CI context must remain named ci")
    ci_job = jobs.get("ci")
    if not isinstance(ci_job, dict) or ci_job.get("name") != "ci" or "permissions" in ci_job:
        raise ValidationError("required CI context must remain named ci")


def validate_repository() -> None:
    validate_dependency_automation_policy()
    validate_workflow_automation_safety()
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
        if expected_source == "pdugan20/skills" and lock_entry.get("ref") != PATRICK_SKILLS_REF:
            raise ValidationError(
                f"locked skill {skill_name} must pin Patrick Skills {PATRICK_SKILLS_REF}"
            )
        if (
            expected_source == "getsentry/XcodeBuildMCP"
            and lock_entry.get("ref") != XCODEBUILDMCP_REF
        ):
            raise ValidationError(
                f"locked skill {skill_name} must pin XcodeBuildMCP {XCODEBUILDMCP_REF}"
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
        "mintlify-docs@patrick-plugins",
        "mintlify-docs@pdugan20-plugins",
        "mintlify-docs@patrick-tools",
        "patrick-workflows@pdugan20-plugins",
        "patrick-workflows@patrick-tools",
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
        new_marketplace = script.index("ensure_marketplace patrick-plugins")
        for retired_id in (
            "mintlify-docs@patrick-plugins",
            "mintlify-docs@pdugan20-plugins",
            "mintlify-docs@patrick-tools",
            "patrick-workflows@pdugan20-plugins",
            "patrick-workflows@patrick-tools",
        ):
            if script.index(retired_id) > new_marketplace:
                raise ValidationError(
                    f"{script_name} must retire {retired_id} before adding its replacement"
                )
        for retired_marketplace in ("pdugan20-plugins", "patrick-tools"):
            if script.index(retired_marketplace) > new_marketplace:
                raise ValidationError(
                    f"{script_name} must retire {retired_marketplace} before adding its replacement"
                )
        if "scripts/reconcile_claude_plugins.py" not in script:
            raise ValidationError(
                f"{script_name} must disable undeclared enabled user-scoped plugins"
            )
        if "ensure_marketplace mintlify-marketplace mintlify/mintlify-claude-plugin" not in script:
            raise ValidationError(f"{script_name} must add Mintlify's canonical marketplace")
        if "ensure_marketplace patrick-plugins pdugan20/plugins" not in script:
            raise ValidationError(f"{script_name} must add Patrick's plugin marketplace")

    for script_name in ("install-codex-plugins.sh", "refresh-codex-plugins.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
        new_marketplace = script.index("ensure_marketplace patrick-plugins")
        for retired_id in (
            "mintlify-docs@patrick-plugins",
            "mintlify-docs@pdugan20-plugins",
            "mintlify-docs@patrick-tools",
            "patrick-workflows@pdugan20-plugins",
            "patrick-workflows@patrick-tools",
        ):
            if script.index(retired_id) > new_marketplace:
                raise ValidationError(
                    f"{script_name} must retire {retired_id} before adding its replacement"
                )
        for retired_marketplace in ("pdugan20-plugins", "patrick-tools"):
            if script.index(retired_marketplace) > new_marketplace:
                raise ValidationError(
                    f"{script_name} must retire {retired_marketplace} before adding its replacement"
                )
        if (
            "ensure_marketplace patrick-plugins https://github.com/pdugan20/plugins.git"
            not in script
        ):
            raise ValidationError(f"{script_name} must add Patrick's plugin marketplace")


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
