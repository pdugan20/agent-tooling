from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "global/hooks/agents_md_context.py"
SPEC = importlib.util.spec_from_file_location("agents_md_context", MODULE_PATH)
assert SPEC and SPEC.loader
agents_md_context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agents_md_context)


def run_hook(stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class AgentsMdContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name).resolve() / "repository"
        (self.repository / ".git").mkdir(parents=True)
        (self.repository / "AGENTS.md").write_text("# Root rules\n\nKeep data synthetic.\n")

    def test_returns_root_agents_md_when_no_claude_file_exists(self) -> None:
        context = agents_md_context.build_context(self.repository)

        self.assertIn("Keep data synthetic.", context)
        self.assertIn(str(self.repository / "AGENTS.md"), context)

    def test_repository_claude_md_takes_precedence(self) -> None:
        for claude_file in ("CLAUDE.md", ".claude/CLAUDE.md"):
            with self.subTest(claude_file=claude_file):
                path = self.repository / claude_file
                path.parent.mkdir(exist_ok=True)
                path.write_text("@AGENTS.md\n")
                self.assertEqual(agents_md_context.build_context(self.repository), "")
                path.unlink()

    def test_local_claude_file_suppresses_only_when_it_imports_agents_md(self) -> None:
        local = self.repository / "CLAUDE.local.md"
        local.write_text("Personal sandbox notes.\n")
        self.assertIn("Keep data synthetic.", agents_md_context.build_context(self.repository))

        local.write_text("@AGENTS.md\n")
        self.assertEqual(agents_md_context.build_context(self.repository), "")

    def test_nested_working_directory_loads_root_first(self) -> None:
        nested = self.repository / "packages" / "ui"
        nested.mkdir(parents=True)
        (nested / "AGENTS.md").write_text("Package rules.\n")

        context = agents_md_context.build_context(nested)

        self.assertLess(context.index("Keep data synthetic."), context.index("Package rules."))

    def test_outside_a_repository_only_the_working_directory_is_read(self) -> None:
        outside = Path(self.temporary.name).resolve() / "loose" / "child"
        outside.mkdir(parents=True)
        (outside.parent / "AGENTS.md").write_text("Parent rules.\n")
        (outside / "AGENTS.md").write_text("Child rules.\n")

        context = agents_md_context.build_context(outside)

        self.assertIn("Child rules.", context)
        self.assertNotIn("Parent rules.", context)

    def test_large_files_are_truncated_with_a_pointer(self) -> None:
        size = agents_md_context.MAX_BYTES_PER_FILE + 100
        (self.repository / "AGENTS.md").write_text("x" * size)

        context = agents_md_context.build_context(self.repository)

        self.assertIn("[Truncated at", context)

    def test_hook_emits_session_start_context_json(self) -> None:
        result = run_hook(json.dumps({"cwd": str(self.repository), "source": "startup"}))

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Keep data synthetic.", output["hookSpecificOutput"]["additionalContext"])

    def test_unreadable_input_never_fails_the_session(self) -> None:
        result = run_hook("not json")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
