"""Checks for linking the Apple skills bundled with Xcode into user skill folders."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from check_skill_ownership import audit
from link_xcode_skills import CONFIG, resolve_names, skill_files

SCRIPT = Path(__file__).with_name("link_xcode_skills.py")


class XcodeSkillTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.app = self.base / "Xcode.app"
        self.resources = self.app / json.loads(CONFIG.read_text())["resources"]
        self.resources.mkdir(parents=True)
        self.target = self.base / "skills"
        self.cache = self.base / "cache"
        self.ship("xctrace", ["overview"])
        self.ship("swiftui-whats-new-27", ["toolbar"])
        self.ship("swiftui-specialist", ["structure"])

    def ship(self, name, references):
        listed = "\n".join(f"- references/{item}.md" for item in references)
        template = f"---\nname: {name}\ndescription: Example\n---\n\n{listed}\n"
        (self.resources / f"{name}.idechatprompttemplate").write_text(template)
        for item in references:
            (self.resources / f"{name}-ref-{item}.md.packaged").write_text(f"# {item}\n")

    def link(self, *args, app=None):
        env = {**os.environ, "AGENT_TOOLING_XCODE_APP": str(app or self.app)}
        command = ["python3", str(SCRIPT), "--target", str(self.target), "--cache", str(self.cache)]
        return subprocess.run(
            [*command, *args], env=env, capture_output=True, text=True, check=False
        )

    def test_selects_listed_skills_and_the_newest_release(self):
        self.ship("swiftui-whats-new-28", ["toolbar"])
        patterns = ["swiftui-whats-new-*", "xctrace", "not-shipped"]
        self.assertEqual(
            resolve_names(patterns, self.resources), ["swiftui-whats-new-28", "xctrace"]
        )

    def test_folder_copies_every_file_from_xcode(self):
        result = self.link()
        self.assertEqual(result.returncode, 0, result.stderr)
        skill = self.target / "xctrace"
        self.assertEqual(skill.readlink(), self.cache / "xctrace")
        # Codex skips a skill whose SKILL.md is a symlink, so the folder holds real files.
        self.assertFalse((skill / "SKILL.md").is_symlink())
        self.assertEqual(
            (skill / "SKILL.md").read_bytes(),
            (self.resources / "xctrace.idechatprompttemplate").read_bytes(),
        )
        self.assertEqual((skill / "references/overview.md").read_text(), "# overview\n")
        self.assertFalse((self.target / "swiftui-specialist").exists())
        self.assertEqual(self.link("--check").returncode, 0)

    def test_xcode_update_is_reported_until_bootstrap_runs(self):
        self.link()
        (self.resources / "xctrace-ref-overview.md.packaged").write_text("# overview v2\n")
        self.assertEqual(self.link("--check").returncode, 1)
        codes = {item["code"] for item in audit([self.target], {}, None, self.cache)["findings"]}
        self.assertEqual(codes, {"xcode-skill-changed-rerun-bootstrap"})
        self.assertEqual(self.link().returncode, 0)
        self.assertEqual(self.link("--check").returncode, 0)
        self.assertEqual(
            (self.target / "xctrace/references/overview.md").read_text(), "# overview v2\n"
        )

    def test_newer_release_replaces_the_older_link(self):
        self.link()
        self.ship("swiftui-whats-new-28", ["toolbar"])
        self.assertEqual(self.link("--check").returncode, 1)
        self.assertEqual(self.link().returncode, 0)
        self.assertFalse((self.target / "swiftui-whats-new-27").is_symlink())
        self.assertTrue((self.target / "swiftui-whats-new-28/SKILL.md").is_file())
        self.assertEqual(self.link("--check").returncode, 0)

    def test_relative_cache_makes_working_links(self):
        env = {**os.environ, "AGENT_TOOLING_XCODE_APP": str(self.app)}
        command = ["python3", str(SCRIPT), "--target", str(self.target), "--cache", "cache"]
        result = subprocess.run(command, env=env, cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        link = (self.target / "xctrace").readlink()
        self.assertTrue(link.is_absolute())
        self.assertEqual(link.resolve(), (self.cache / "xctrace").resolve())
        self.assertTrue((self.target / "xctrace/SKILL.md").is_file())

    def test_existing_path_is_preserved(self):
        (self.target / "xctrace").mkdir(parents=True)
        result = self.link()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing to replace existing path", result.stderr)
        self.assertEqual(list((self.target / "xctrace").iterdir()), [])

    def test_missing_xcode_changes_nothing(self):
        result = self.link(app=self.base / "Missing.app")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Xcode isn't installed", result.stdout)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.link("--check", app=self.base / "Missing.app").returncode, 0)

    def test_reference_xcode_does_not_ship_is_an_error(self):
        (self.resources / "xctrace-ref-overview.md.packaged").unlink()
        with self.assertRaisesRegex(ValueError, "references/overview.md"):
            skill_files("xctrace", self.resources)

    def test_doctor_accepts_xcode_copies_and_rejects_other_sources(self):
        self.link()
        report = audit([self.target], {}, None, self.cache)
        self.assertTrue(report["ok"], report["findings"])
        self.assertEqual({entry["state"] for entry in report["entries"]}, {"linked-from-xcode"})
        manifest = self.cache / "xctrace/.xcode-source.json"
        manifest.write_text(json.dumps({"files": {"SKILL.md": str(self.base / "outside.md")}}))
        codes = {item["code"] for item in audit([self.target], {}, None, self.cache)["findings"]}
        self.assertIn("unreadable-or-external-resource", codes)

    def test_doctor_reports_files_added_to_a_copy(self):
        self.link()
        (self.cache / "xctrace/references/extra.md").write_text("added by hand")
        codes = {item["code"] for item in audit([self.target], {}, None, self.cache)["findings"]}
        self.assertEqual(codes, {"xcode-skill-changed-rerun-bootstrap"})


if __name__ == "__main__":
    unittest.main()
