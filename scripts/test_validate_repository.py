from __future__ import annotations

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
                "pdugan20/patrick-workflows",
            )
            self.assertEqual(
                skills_lock["skills"][skill_name]["ref"],
                validate_repository.PATRICK_WORKFLOWS_REF,
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
            self.assertFalse((home / ".claude").exists())

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


if __name__ == "__main__":
    unittest.main()
