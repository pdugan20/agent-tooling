from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_skill_snapshots.mjs"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class SkillSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.skill = self.root / ".agents/skills/demo"
        (self.skill / "references").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: demo\n---\n")
        (self.skill / "references/guide.md").write_text("original\n")
        (self.root / "config").mkdir()
        self.write_exceptions({})
        self.write_lock(self.installed_hash())

    def installed_hash(self) -> str:
        output = run(self.root, "--print")
        self.assertEqual(output.returncode, 0, output.stderr)
        return json.loads(output.stdout)["demo"]

    def write_lock(self, computed_hash: str) -> None:
        lock = {"version": 1, "skills": {"demo": {"computedHash": computed_hash}}}
        (self.root / "skills-lock.json").write_text(json.dumps(lock))

    def write_exceptions(self, exceptions: dict) -> None:
        path = self.root / "config/skill-snapshot-hashes.json"
        path.write_text(json.dumps({"schemaVersion": 1, "exceptions": exceptions}))

    def test_repository_snapshots_match_the_lock(self) -> None:
        output = run(ROOT)
        self.assertEqual(output.returncode, 0, output.stderr)

    def test_an_edited_snapshot_fails(self) -> None:
        self.assertEqual(run(self.root).returncode, 0)
        (self.skill / "references/guide.md").write_text("changed\n")
        output = run(self.root)
        self.assertEqual(output.returncode, 1)
        self.assertIn("demo: snapshot files no longer produce the skills-lock.json", output.stderr)

    def test_links_and_dependency_installs_do_not_change_the_hash(self) -> None:
        expected = self.installed_hash()
        (self.skill / "node_modules/pkg").mkdir(parents=True)
        (self.skill / "node_modules/pkg/index.js").write_text("x")
        (self.skill / "linked").symlink_to("references")
        self.assertEqual(self.installed_hash(), expected)

    def test_exception_pins_the_installed_tree(self) -> None:
        lock_hash = "f" * 64
        self.write_lock(lock_hash)
        self.assertEqual(run(self.root).returncode, 1)
        exception = {"lockHash": lock_hash, "installedTreeHash": self.installed_hash()}
        self.write_exceptions({"demo": exception})
        self.assertEqual(run(self.root).returncode, 0)

        (self.skill / "SKILL.md").write_text("---\nname: demo\n---\nedited\n")
        output = run(self.root)
        self.assertEqual(output.returncode, 1)
        self.assertIn("snapshot files changed since the exception was recorded", output.stderr)

    def test_stale_or_orphaned_exceptions_fail(self) -> None:
        installed = self.installed_hash()
        self.write_exceptions({"demo": {"lockHash": installed, "installedTreeHash": installed}})
        self.assertIn("remove its exception", run(self.root).stderr)

        self.write_lock("e" * 64)
        self.write_exceptions({"demo": {"lockHash": "f" * 64, "installedTreeHash": installed}})
        self.assertIn("lock entry changed after the exception", run(self.root).stderr)

        self.write_lock(installed)
        self.write_exceptions({"gone": {"lockHash": "a", "installedTreeHash": "b"}})
        orphaned = run(self.root).stderr
        self.assertIn("gone: config/skill-snapshot-hashes.json lists a skill", orphaned)

    def test_unlocked_skill_folders_fail(self) -> None:
        (self.root / ".agents/skills/extra").mkdir()
        (self.root / ".agents/skills/extra/notes.md").write_text("not installed by Skills CLI\n")
        output = run(self.root)
        self.assertEqual(output.returncode, 1)
        self.assertIn("extra: .agents/skills/extra has no skills-lock.json entry", output.stderr)


if __name__ == "__main__":
    unittest.main()
