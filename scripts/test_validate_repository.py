from __future__ import annotations

import copy
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import validate_repository


class RepositoryValidationTests(unittest.TestCase):
    def test_current_repository_is_valid(self) -> None:
        validate_repository.validate_repository()

    def test_dependency_automation_active_policy_is_fail_closed(self) -> None:
        validate_repository.validate_dependency_automation_policy()
        policy = validate_repository.load_json(validate_repository.RENOVATE_CONFIG)

        unsafe_variants = []
        for description, mutate in (
            ("disabled", lambda value: value.__setitem__("enabled", False)),
            (
                "default dashboard gate removed",
                lambda value: value["packageRules"].pop(0),
            ),
            (
                "unowned manager",
                lambda value: value["enabledManagers"].append("pre-commit"),
            ),
            (
                "Renovate security PRs",
                lambda value: value["vulnerabilityAlerts"].__setitem__("enabled", True),
            ),
            (
                "lockfile automerge",
                lambda value: value["lockFileMaintenance"].__setitem__("automerge", True),
            ),
            (
                "stable matcher admits v-prefixed pre-1.0 versions",
                lambda value: value["packageRules"][1].__setitem__(
                    "matchCurrentVersion", "!/^0\\./"
                ),
            ),
            (
                "pre-1.0 matcher admits prereleases",
                lambda value: value["packageRules"][2].__setitem__(
                    "matchCurrentVersion", "/^0\\./"
                ),
            ),
            (
                "short Actions quarantine",
                lambda value: value["packageRules"][3].__setitem__("minimumReleaseAge", "7 days"),
            ),
            (
                "Actions matcher admits v-prefixed pre-1.0 releases",
                lambda value: value["packageRules"][3].__setitem__(
                    "matchCurrentVersion", "/^v?\\d+\\.\\d+\\.\\d+$/"
                ),
            ),
            (
                "pre-1.0 minor automerge",
                lambda value: value["packageRules"][4].__setitem__("automerge", True),
            ),
            (
                "major automerge",
                lambda value: value["packageRules"][5].__setitem__("automerge", True),
            ),
            (
                "unsafe terminal gate removed",
                lambda value: value["packageRules"].pop(),
            ),
            (
                "unsafe terminal gate constrained to npm",
                lambda value: value["packageRules"][-1].__setitem__("matchManagers", ["npm"]),
            ),
            (
                "unsafe terminal gate allows automerge",
                lambda value: value["packageRules"][-1].__setitem__("automerge", True),
            ),
            (
                "unsafe terminal gate bypasses dashboard approval",
                lambda value: value["packageRules"][-1].__setitem__(
                    "dependencyDashboardApproval", False
                ),
            ),
        ):
            candidate = copy.deepcopy(policy)
            mutate(candidate)
            unsafe_variants.append((description, candidate))

        for rule_index, rule_name in ((1, "stable"), (2, "pre-1.0")):
            for update_type in ("digest", "pin", "pinDigest", "lockFileMaintenance"):
                candidate = copy.deepcopy(policy)
                candidate["packageRules"][rule_index]["matchUpdateTypes"].append(update_type)
                unsafe_variants.append((f"{rule_name} {update_type} automerge", candidate))

        dependabot = validate_repository.DEPENDABOT_CONFIG.read_text(encoding="utf-8")
        for description, candidate in unsafe_variants:
            with (
                self.subTest(description=description),
                self.assertRaises(validate_repository.ValidationError),
            ):
                validate_repository.validate_dependency_automation_policy(
                    candidate,
                    dependabot,
                )

    def test_dependency_automation_automerge_scope_is_exact(self) -> None:
        policy = validate_repository.load_json(validate_repository.RENOVATE_CONFIG)
        rules = policy["packageRules"]

        self.assertEqual(
            rules[1]["matchCurrentVersion"],
            "/^[1-9]\\d*\\.\\d+\\.\\d+$/",
        )
        self.assertEqual(rules[1]["matchUpdateTypes"], ["patch", "minor"])
        self.assertEqual(rules[2]["matchCurrentVersion"], "/^0\\.\\d+\\.\\d+$/")
        self.assertEqual(rules[2]["matchUpdateTypes"], ["patch"])
        self.assertEqual(
            rules[3]["matchCurrentVersion"],
            "/^v?[1-9]\\d*\\.\\d+\\.\\d+$/",
        )
        self.assertEqual(rules[3]["matchUpdateTypes"], ["patch", "minor"])
        self.assertEqual(
            rules[-1],
            {
                "description": "Unsafe update types require manual approval",
                "matchUpdateTypes": ["digest", "pin", "pinDigest", "lockFileMaintenance"],
                "dependencyDashboardApproval": True,
                "automerge": False,
            },
        )

    def test_dependabot_routine_ownership_transfer_is_fail_closed(self) -> None:
        policy = validate_repository.load_json(validate_repository.RENOVATE_CONFIG)
        dependabot = validate_repository.DEPENDABOT_CONFIG.read_text(encoding="utf-8")
        parsed = validate_repository.load_yaml(dependabot)
        for update in parsed["updates"]:
            self.assertNotIn("ignore", update)
        actions_limit = dependabot.rfind("open-pull-requests-limit: 0")
        self.assertGreater(actions_limit, 0)
        variants = {
            "npm routine updates": dependabot.replace(
                "open-pull-requests-limit: 0", "open-pull-requests-limit: 1", 1
            ),
            "Actions routine updates": dependabot[:actions_limit]
            + dependabot[actions_limit:].replace(
                "open-pull-requests-limit: 0", "open-pull-requests-limit: 1", 1
            ),
            "duplicate npm routine limit": dependabot.replace(
                "    open-pull-requests-limit: 0\n",
                "    open-pull-requests-limit: 0\n    open-pull-requests-limit : 5\n",
                1,
            ),
            "flow-style npm routine limit": dependabot.replace(
                "    open-pull-requests-limit: 0\n",
                "    metadata: {open-pull-requests-limit: 5}\n",
                1,
            ),
            "npm security ignore": dependabot.replace(
                "    open-pull-requests-limit: 0\n",
                '    open-pull-requests-limit: 0\n    ignore:\n      - dependency-name: "*"\n',
                1,
            ),
            "Actions security ignore": dependabot[:actions_limit]
            + dependabot[actions_limit:].replace(
                "open-pull-requests-limit: 0\n",
                'open-pull-requests-limit: 0\n    ignore:\n      - dependency-name: "*"\n',
                1,
            ),
            "schema drift": dependabot.replace("version: 2", "version: 1", 1),
            "quoted duplicate schema": dependabot + '\n"version": 1\n',
            "quoted duplicate updates": dependabot + '\n"updates": []\n',
            "extra ecosystem": dependabot
            + "\n  - package-ecosystem: pip\n"
            + "    directory: /\n"
            + "    target-branch: main\n"
            + "    open-pull-requests-limit: 0\n",
        }

        for description, source in variants.items():
            with (
                self.subTest(description=description),
                self.assertRaises(validate_repository.ValidationError),
            ):
                validate_repository.validate_dependency_automation_policy(policy, source)

    def test_workflow_action_policy_accepts_legitimate_pinned_updates(self) -> None:
        source = """jobs:
  test:
    env:
      WORD: "uses"
      PIN_DOCUMENTATION: |
        uses: actions/checkout@cccccccccccccccccccccccccccccccccccccccc # v9.9.9
    steps:
      - uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
"""
        references, errors = validate_repository.action_reference_errors({"fixture.yml": source})

        self.assertEqual(
            references,
            ["actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3"],
        )
        self.assertEqual(errors, [])

        reusable = (
            "jobs:\n  test:\n"
            "    uses: owner/repository/.github/workflows/test.yml@"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb # v1.2.3\n"
        )
        references, errors = validate_repository.action_reference_errors({"fixture.yml": reusable})
        self.assertEqual(
            references,
            [
                "owner/repository/.github/workflows/test.yml@"
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb # v1.2.3"
            ],
        )
        self.assertEqual(errors, [])

    def test_workflow_action_policy_rejects_floating_and_comment_spoofing(self) -> None:
        variants = {
            "spaced key": """jobs:
  test:
    steps:
      # - uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
      - uses : actions/checkout@v7
""",
            "flow key": """jobs:
  test:
    steps:
      - {uses: actions/setup-node@v6}
""",
            "explicit key": """jobs:
  test:
    steps:
      - name: Explicit mapping syntax
        ? uses
        : actions/checkout@v6
""",
            "multiline comment spoof": """env:
  PIN_PROOF: |
    uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
jobs:
  test:
    steps:
      - {uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}
""",
            "escaped uses key with multiline scalar spoof": """env:
  PIN_PROOF: "uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3"
jobs:
  test:
    steps:
      - "us\\u0065s": actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
""",
            "plain-scalar pipe with multiline scalar spoof": """env:
  PIN_PROOF: "
    uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
    "
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out |
        uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
""",
            "alias uses key": """env:
  ACTION_KEY: &action_key uses
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - ? *action_key
        : actions/checkout@v7
      - uses: actions/setup-node@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v6.1.0
""",
            "tagged uses key": """jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - !!str uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
""",
            "anchored uses key": """jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - &action_key uses: actions/checkout@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # v7.2.3
""",
        }
        for description, source in variants.items():
            with self.subTest(description=description):
                _, errors = validate_repository.action_reference_errors({"fixture.yml": source})
                self.assertTrue(errors)

    def test_workflow_action_discovery_includes_yaml_and_composite_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflows = root / ".github/workflows"
            actions = root / ".github/actions/example"
            templates = root / ".github/workflow-templates"
            workflows.mkdir(parents=True)
            actions.mkdir(parents=True)
            templates.mkdir(parents=True)
            workflows.joinpath("fixture.yaml").write_text(
                "steps:\n  - uses : actions/checkout@v7\n",
                encoding="utf-8",
            )
            actions.joinpath("action.yml").write_text(
                "runs:\n  steps:\n    - uses: actions/setup-node@v6\n",
                encoding="utf-8",
            )
            root.joinpath("action.yaml").write_text(
                "runs:\n  steps:\n    - uses: owner/repository/subpath@v1\n",
                encoding="utf-8",
            )
            templates.joinpath("template.yaml").write_text(
                "steps:\n  - uses: actions/checkout@v6\n",
                encoding="utf-8",
            )

            with (
                mock.patch.object(validate_repository, "ROOT", root),
                mock.patch.object(validate_repository, "WORKFLOWS_ROOT", workflows),
                mock.patch.object(validate_repository, "ACTIONS_ROOT", root / ".github/actions"),
                mock.patch.object(
                    validate_repository,
                    "WORKFLOW_TEMPLATE_ROOTS",
                    (root / "workflow-templates", templates),
                ),
            ):
                sources = validate_repository.github_action_sources()

            self.assertEqual(
                set(sources),
                {
                    ".github/workflows/fixture.yaml",
                    ".github/actions/example/action.yml",
                    "action.yaml",
                    ".github/workflow-templates/template.yaml",
                },
            )
            references, errors = validate_repository.action_reference_errors(sources)
            self.assertEqual(len(references), 4)
            self.assertEqual(len(errors), 5)

    def test_ci_permissions_and_required_job_are_fail_closed(self) -> None:
        sources = validate_repository.github_action_sources()
        ci_path = ".github/workflows/ci.yml"
        unsafe_variants = {
            "job write-all": sources[ci_path].replace(
                "    runs-on: ubuntu-latest\n",
                "    runs-on: ubuntu-latest\n    permissions: write-all\n",
                1,
            ),
            "job flow write": sources[ci_path].replace(
                "    runs-on: ubuntu-latest\n",
                "    runs-on: ubuntu-latest\n    permissions: {contents: write}\n",
                1,
            ),
            "job explicit-key write": sources[ci_path].replace(
                "    runs-on: ubuntu-latest\n",
                "    runs-on: ubuntu-latest\n    ? permissions\n    : write-all\n",
                1,
            ),
            "step spoofed name": sources[ci_path]
            .replace("  ci:\n", "  tests:\n", 1)
            .replace("    name: ci\n", "    name: tests\n", 1)
            .replace(
                "      - name: Check out repository\n",
                "      - name: ci\n        run: echo spoof\n      - name: Check out repository\n",
                1,
            ),
        }
        for description, ci in unsafe_variants.items():
            candidate = dict(sources)
            candidate[ci_path] = ci
            with (
                self.subTest(description=description),
                self.assertRaises(validate_repository.ValidationError),
            ):
                validate_repository.validate_workflow_automation_safety(candidate)

    def test_release_workflow_rejects_non_tag_trigger(self) -> None:
        workflows = validate_repository.github_action_sources()
        release_path = ".github/workflows/release.yml"
        workflows[release_path] = workflows[release_path].replace(
            "on:\n",
            "on:\n  workflow_dispatch:\n",
            1,
        )

        with self.assertRaisesRegex(validate_repository.ValidationError, "tag-only"):
            validate_repository.validate_workflow_automation_safety(workflows)

    def test_release_installs_yaml_parser_before_repository_validation(self) -> None:
        workflows = validate_repository.github_action_sources()
        release_path = ".github/workflows/release.yml"
        install = "      - name: Install npm dependencies\n        run: npm ci\n"
        validate = (
            "      - name: Validate release tag\n"
            '        run: python scripts/validate_repository.py --release-tag "$GITHUB_REF_NAME"\n'
        )
        self.assertIn(install, workflows[release_path])
        self.assertIn(validate, workflows[release_path])
        workflows[release_path] = workflows[release_path].replace(
            f"{install}\n{validate}",
            f"{validate}\n{install}",
            1,
        )

        with self.assertRaisesRegex(validate_repository.ValidationError, "install npm"):
            validate_repository.validate_workflow_automation_safety(workflows)

    def test_superpowers_configuration_tracks_upstream_and_fork(self) -> None:
        configuration = validate_repository.load_json(validate_repository.SUPERPOWERS_CONFIG)

        self.assertEqual(configuration["upstreamVersion"], "6.2.0")
        self.assertEqual(configuration["forkVersion"], "6.2.0-config.2")
        self.assertEqual(configuration["marketplace"], "superpowers-configured")
        self.assertIn("test-driven-development", configuration["explicitOnlySkills"])
        self.assertIn("systematic-debugging", configuration["automaticSkills"])

    def test_managed_skills_are_locked_with_source_provenance(self) -> None:
        skills_lock = validate_repository.load_json(validate_repository.ROOT / "skills-lock.json")

        self.assertEqual(set(skills_lock["skills"]), set(validate_repository.UPSTREAM_SKILLS))
        for skill_name in validate_repository.CUSTOM_SKILLS:
            self.assertEqual(
                skills_lock["skills"][skill_name]["source"],
                "pdugan20/skills",
            )
            self.assertEqual(
                skills_lock["skills"][skill_name]["ref"],
                validate_repository.PATRICK_SKILLS_REF,
            )
        self.assertEqual(
            skills_lock["skills"]["xcodebuildmcp"]["ref"],
            validate_repository.XCODEBUILDMCP_REF,
        )
        self.assertEqual(
            set((validate_repository.ROOT / ".agents/skills").glob("*/skills/*/SKILL.md")),
            {validate_repository.ROOT / ".agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"},
        )

    def test_bootstrap_honors_claude_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            home = temporary_root / "home"
            claude_profile = temporary_root / "active-claude"
            home.mkdir()
            (home / ".agents/skills").mkdir(parents=True)
            claude_profile.joinpath("skills").mkdir(parents=True)
            retired_target = validate_repository.ROOT / ".agents/skills/production-hardening"
            (home / ".agents/skills/production-hardening").symlink_to(retired_target)
            (claude_profile / "skills/production-hardening").symlink_to(retired_target)
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "CLAUDE_CONFIG_DIR": str(claude_profile),
                }
            )

            subprocess.run(
                ["bash", str(validate_repository.ROOT / "scripts/bootstrap.sh")],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(
                (claude_profile / "CLAUDE.md").readlink(),
                validate_repository.ROOT / "global/AGENTS.md",
            )
            self.assertTrue((claude_profile / "skills/code-native-ui-ideation").is_symlink())
            self.assertFalse((home / ".agents/skills/production-hardening").is_symlink())
            self.assertFalse((claude_profile / "skills/production-hardening").is_symlink())
            self.assertFalse((home / ".claude").exists())

    def test_retired_marketplaces_are_removed_before_replacement_registration(self) -> None:
        for runtime in ("claude", "codex"):
            for operation in ("install", "refresh"):
                script = (
                    validate_repository.ROOT / "scripts" / f"{operation}-{runtime}-plugins.sh"
                ).read_text(encoding="utf-8")
                replacement = script.index("ensure_marketplace patrick-plugins")
                for retired_marketplace in ("pdugan20-plugins", "patrick-tools"):
                    self.assertLess(script.index(retired_marketplace), replacement)
                for retired_plugin in (
                    "mintlify-docs@patrick-plugins",
                    "mintlify-docs@pdugan20-plugins",
                    "mintlify-docs@patrick-tools",
                    "patrick-workflows@pdugan20-plugins",
                    "patrick-workflows@patrick-tools",
                ):
                    self.assertLess(script.index(retired_plugin), replacement)

    def test_release_tag_must_match_repository_version(self) -> None:
        with (
            mock.patch.object(validate_repository, "repository_version", return_value="1.2.3"),
            mock.patch.object(validate_repository, "CHANGELOG") as changelog,
        ):
            changelog.read_text.return_value = "## [1.2.3] - 2026-07-28\n"
            self.assertEqual(
                validate_repository.validate_release_tag("v1.2.3"),
                "1.2.3",
            )
            with self.assertRaisesRegex(validate_repository.ValidationError, "does not match"):
                validate_repository.validate_release_tag("v1.2.4")

    def test_release_tag_rejects_other_namespaces(self) -> None:
        with self.assertRaisesRegex(validate_repository.ValidationError, "must use"):
            validate_repository.validate_release_tag("patrick-delivery-v0.2.0")

    def test_release_tag_requires_changelog_section(self) -> None:
        with (
            mock.patch.object(validate_repository, "repository_version", return_value="1.2.3"),
            mock.patch.object(validate_repository, "CHANGELOG") as changelog,
        ):
            changelog.read_text.return_value = "## [Unreleased]\n"
            with self.assertRaisesRegex(validate_repository.ValidationError, r"no \[1.2.3\]"):
                validate_repository.validate_release_tag("v1.2.3")

    def test_prose_counts_are_rejected(self) -> None:
        # The README claimed "twenty-one skills" while twenty-two were locked. Prose has
        # no gate, so the count silently rotted.
        self.assertIsNotNone(validate_repository.PROSE_COUNT_RE.search("All twenty-two skills are"))
        self.assertIsNotNone(validate_repository.PROSE_COUNT_RE.search("the other nine plugins"))
        self.assertIsNotNone(validate_repository.PROSE_COUNT_RE.search("22 skills are installed"))

    def test_prose_counts_ignore_unrelated_nouns(self) -> None:
        self.assertIsNone(validate_repository.PROSE_COUNT_RE.search("twelve commits scanned"))

    def test_dated_measurements_are_exempt(self) -> None:
        # A measurement records a past observation and does not drift.
        line = "Measured 2026-08-17: twelve skills were set to `on`."
        self.assertIsNotNone(validate_repository.MEASUREMENT_RE.search(line))

    def test_current_repository_has_no_prose_counts(self) -> None:
        validate_repository.validate_prose_counts()


if __name__ == "__main__":
    unittest.main()
