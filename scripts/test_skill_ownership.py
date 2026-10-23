"""Regression checks for complete-resource ownership and recoverability."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_skill_ownership import audit, tree_files, tree_hash


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.installed = self.root / "installed"
        self.installed.mkdir()
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("---\nname: example\ndescription: Example\n---\n")
        (self.source / "reference.md").write_text("Useful supporting source")
        (self.installed / "example").symlink_to(self.source, target_is_directory=True)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.source), *args], capture_output=True, check=True)

    def codes(self, ledger=None):
        return {item["code"] for item in audit([self.installed], ledger or {})["findings"]}

    def test_untracked_support_file_is_detected(self):
        self.git("init", "-q")
        self.git("add", "SKILL.md")
        self.assertIn("untracked-resources", self.codes())
        self.git("add", "reference.md")
        self.assertNotIn("untracked-resources", self.codes())

    def test_resource_drift_is_not_hidden_by_unchanged_entrypoint(self):
        ledger = {
            "bindings": [
                {
                    "path": str(self.installed / "example"),
                    "treeSha256": tree_hash(tree_files(self.source)),
                }
            ]
        }
        (self.source / "reference.md").write_text("changed")
        self.assertIn("resource-drift", self.codes(ledger))

    def test_unreadable_nested_directory_fails_instead_of_pinning_a_partial_tree(self):
        references = self.source / "references"
        references.mkdir()
        (references / "guide.md").write_text("Required runtime instructions")
        self.git("init", "-q")
        self.git("add", ".")
        self.assertTrue(audit([self.installed], {})["ok"])

        original_scandir = os.scandir

        def unreadable_scandir(path):
            if Path(path).resolve() == references.resolve():
                raise PermissionError("Cannot read nested resources")
            return original_scandir(path)

        with patch("check_skill_ownership.os.scandir", side_effect=unreadable_scandir):
            report = audit([self.installed], {})

        self.assertFalse(report["ok"])
        self.assertEqual(report["entries"], [])
        self.assertEqual(report["findings"][0]["code"], "unreadable-or-external-resource")

    def test_broken_link_and_divergent_duplicate(self):
        (self.installed / "broken").symlink_to(self.root / "missing")
        another = self.root / "another"
        (another / "example").mkdir(parents=True)
        (another / "example/SKILL.md").write_text("different")
        report = audit([self.installed, another], {})
        codes = {item["code"] for item in report["findings"]}
        self.assertTrue({"broken-link", "divergent-duplicate"} <= codes)

    def test_external_resource_link_is_not_claimed_as_pinned(self):
        external = self.root / "external.md"
        external.write_text("external mutable resource")
        (self.source / "external.md").symlink_to(external)
        self.assertIn("unreadable-or-external-resource", self.codes())

    def test_recovery_must_match_all_bytes_and_be_tracked(self):
        recovery = self.root / "recovery"
        recovery.mkdir()
        for name in ("SKILL.md", "reference.md"):
            (recovery / name).write_bytes((self.source / name).read_bytes())
        subprocess.run(["git", "-C", str(recovery), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(recovery), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(recovery),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "Fixture",
            ],
            check=True,
        )
        binding = {
            "path": str(self.installed / "example"),
            "resolvedSource": str(self.source),
            "owner": "upstream/example",
            "intendedScope": "pilot",
            "treeSha256": tree_hash(tree_files(self.source)),
            "recoverySource": str(recovery),
        }
        self.assertNotIn("untracked-resources", self.codes({"bindings": [binding]}))
        (recovery / "reference.md").write_text("wrong")
        self.assertIn("recovery-mismatch", self.codes({"bindings": [binding]}))

    def test_generated_caches_do_not_cause_drift(self):
        before = tree_hash(tree_files(self.source))
        (self.source / "__pycache__").mkdir()
        (self.source / "__pycache__/generated.pyc").write_bytes(b"generated")
        self.assertEqual(before, tree_hash(tree_files(self.source)))

    def test_missing_explicit_root_fails_but_optional_legacy_root_can_be_absent(self):
        missing = self.root / "misspelled"
        report = audit([missing], {})
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["code"], "missing-configured-root")
        self.assertTrue(audit([missing], {}, {missing})["ok"])


if __name__ == "__main__":
    unittest.main()
