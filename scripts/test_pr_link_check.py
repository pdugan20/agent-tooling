from __future__ import annotations

import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "global/hooks/pr_link_check.py"
SPEC = importlib.util.spec_from_file_location("pr_link_check", MODULE_PATH)
assert SPEC and SPEC.loader
pr_link_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pr_link_check)

REPOS = {"acme/app"}
GH = "https://github.com/acme/app/pull/{n}"
LR = "https://linear.review/acme/app/pull/{n}"


def pair(number: int) -> str:
    return f"[#{number}]({GH.format(n=number)}) · [Linear review]({LR.format(n=number)})"


class FindProblemsTests(unittest.TestCase):
    def test_link_pairs_pass(self) -> None:
        text = f"Review {pair(1201)} and {pair(1202)} before the batch."
        self.assertEqual(pr_link_check.find_problems(text, REPOS), [])

    def test_bare_number_in_prose_or_table_is_flagged(self) -> None:
        table = "| PR | State |\n|---|---|\n| #1202 | green |"
        text = f"{pair(1201)} is ready.\n\n{table}\n\nAfter #1203 merges."
        problems = pr_link_check.find_problems(text, REPOS)
        self.assertEqual(problems, ["bare numbers with no link: #1202, #1203"])

    def test_github_link_without_linear_review_is_flagged_for_indexed_repos(self) -> None:
        text = f"See [#1201]({GH.format(n=1201)})."
        problems = pr_link_check.find_problems(text, REPOS)
        self.assertEqual(problems, ["GitHub link with no Linear review link: acme/app#1201"])

    def test_github_link_alone_passes_for_other_repos(self) -> None:
        text = "See [#87](https://github.com/someone/tools/pull/87)."
        self.assertEqual(pr_link_check.find_problems(text, REPOS), [])

    def test_each_mention_needs_its_own_pair(self) -> None:
        row = f"| [#1201]({GH.format(n=1201)}) | green |"
        text = f"Review {pair(1201)}.\n\n| PR | State |\n|---|---|\n{row}"
        problems = pr_link_check.find_problems(text, REPOS)
        self.assertEqual(problems, ["GitHub link with no Linear review link: acme/app#1201"])

    def test_issue_references_are_not_pull_requests(self) -> None:
        text = "The bug is tracked in issue #1201 and Issues #1202; no pull request exists yet."
        self.assertEqual(pr_link_check.find_problems(text, REPOS), [])

    def test_code_is_exempt(self) -> None:
        text = (
            "Paste this:\n\n```\n" + GH.format(n=1201) + "\n#1202\n```\n\nThe `#1203` label stays."
        )
        self.assertEqual(pr_link_check.find_problems(text, REPOS), [])

    def test_headings_entities_and_short_numbers_pass(self) -> None:
        text = (
            "## Results\n\nThe #1 risk is &#1234; noise in [docs](https://example.com/page#1234)."
        )
        self.assertEqual(pr_link_check.find_problems(text, REPOS), [])


class MainTests(unittest.TestCase):
    def run_hook(self, payload: object) -> tuple[int, str, str]:
        stdin = io.StringIO(payload if isinstance(payload, str) else json.dumps(payload))
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.object(pr_link_check.sys, "stdin", stdin),
            mock.patch.object(pr_link_check.sys, "stdout", stdout),
            mock.patch.object(pr_link_check.sys, "stderr", stderr),
            mock.patch.object(pr_link_check, "load_repos", return_value=REPOS),
        ):
            code = pr_link_check.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_blocks_once_with_reason_on_stderr(self) -> None:
        code, stdout, stderr = self.run_hook({"last_assistant_message": "Merge #1201 next."})
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("#1201", stderr)

    def test_allows_the_continued_turn_through(self) -> None:
        payload = {"last_assistant_message": "Merge #1201 next.", "stop_hook_active": True}
        self.assertEqual(self.run_hook(payload), (0, "", ""))

    def test_clean_reply_and_bad_input_pass_silently(self) -> None:
        self.assertEqual(
            self.run_hook({"last_assistant_message": f"Merge {pair(1201)}."}), (0, "", "")
        )
        self.assertEqual(self.run_hook("not json"), (0, "", ""))
        self.assertEqual(self.run_hook({"last_assistant_message": None}), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
