from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "global/hooks/agent_push_scope.py"
SPEC = importlib.util.spec_from_file_location("agent_push_scope", MODULE_PATH)
assert SPEC and SPEC.loader
hook = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = hook
SPEC.loader.exec_module(hook)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


class Repository:
    """A clone of a local bare origin whose default branch is main."""

    def __init__(self, root: Path) -> None:
        self.origin = root / "origin.git"
        self.path = root / "work"
        git(root, "init", "--quiet", "--bare", "--initial-branch=main", str(self.origin))
        git(root, "clone", "--quiet", str(self.origin), str(self.path))
        for key, value in (("user.name", "Test"), ("user.email", "test@example.com")):
            git(self.path, "config", key, value)
        git(self.path, "checkout", "--quiet", "-b", "main")
        self.write("README.md", "hello\n")
        self.write("package.json", json.dumps({"version": "1.0.0", "scripts": {"lint": "x"}}))
        self.commit("initial")
        git(self.path, "push", "--quiet", "-u", "origin", "main")
        git(self.path, "remote", "set-head", "origin", "main")

    def write(self, name: str, content: str) -> None:
        target = self.path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self, message: str) -> None:
        git(self.path, "add", "-A")
        git(self.path, "commit", "--quiet", "-m", message)

    def branch(self, name: str, start: str = "main") -> None:
        git(self.path, "checkout", "--quiet", "-b", name, start)

    def check(self, command: str = "git push -u origin HEAD") -> str | None:
        event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.path)}
        return hook.check(event)


class AgentPushScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Repository(Path(self.directory.name))
        self.pull_requests: dict[str, dict] = {}
        patcher = mock.patch.object(hook, "pull_request", self.fake_pull_request)
        patcher.start()
        self.addCleanup(patcher.stop)

    def fake_pull_request(self, cwd: str, branch: str) -> dict | None:
        return self.pull_requests.get(branch)

    def test_commands_without_a_push_never_start_a_subprocess(self) -> None:
        with mock.patch.object(hook, "run", side_effect=AssertionError("ran a subprocess")):
            self.assertIsNone(self.repo.check("git commit -m 'push the button'"))
            self.assertIsNone(self.repo.check("npm test"))
            event = {"tool_name": "Read", "tool_input": {"command": "git push"}}
            self.assertIsNone(hook.check(event))

    def test_product_changes_push_without_a_declaration(self) -> None:
        self.repo.branch("feat/app")
        self.repo.write("src/app.ts", "export {}\n")
        self.repo.commit("app")
        self.assertIsNone(self.repo.check())

    def test_undeclared_ci_buildkit_and_tool_version_changes_are_refused(self) -> None:
        self.repo.branch("feat/app")
        self.repo.write(".circleci/config.yml", "version: 2.1\n")
        self.repo.write(".github/workflows/ci.yml", "on: push\n")
        self.repo.write(".circleci/buildkit/restore.sh", "echo\n")
        self.repo.write(".circleci/ci-tool-versions.env", "NODE=24\n")
        self.repo.commit("carry old config")

        reason = self.repo.check()

        self.assertIsNotNone(reason)
        self.assertIn("ci-config: .circleci/config.yml; .github/workflows/ci.yml", reason)
        self.assertIn("buildkit: .circleci/buildkit/restore.sh", reason)
        self.assertIn("ci-tool-versions: .circleci/ci-tool-versions.env", reason)
        self.assertIn("Agent-Scope: ci-config, buildkit, ci-tool-versions", reason)

    def test_commit_trailer_declares_intended_scope(self) -> None:
        self.repo.branch("ci/validate")
        self.repo.write(".circleci/config.yml", "version: 2.1\n")
        self.repo.commit("Validate config\n\nAgent-Scope: ci-config")
        self.assertIsNone(self.repo.check())

    def test_partial_declaration_still_refuses_the_rest(self) -> None:
        self.repo.branch("ci/validate")
        self.repo.write(".circleci/config.yml", "version: 2.1\n")
        self.repo.write(".circleci/buildkit/bake.sh", "echo\n")
        self.repo.commit("Validate config\n\nAgent-Scope: ci-config")
        reason = self.repo.check()
        self.assertIsNotNone(reason)
        self.assertIn("buildkit", reason)
        self.assertNotIn("ci-config:", reason)

    def test_pull_request_body_declares_intended_scope(self) -> None:
        self.repo.branch("ci/validate")
        self.repo.write(".github/workflows/ci.yml", "on: push\n")
        self.repo.commit("workflow")
        self.pull_requests["ci/validate"] = {
            "baseRefName": "main",
            "body": "Adds a workflow.\n\nAgent-Scope: ci-config\n",
        }
        self.assertIsNone(self.repo.check())

    def test_package_script_changes_are_refused_but_other_fields_are_not(self) -> None:
        self.repo.branch("chore/version")
        self.repo.write("package.json", json.dumps({"version": "2.0.0", "scripts": {"lint": "x"}}))
        self.repo.commit("bump")
        self.assertIsNone(self.repo.check())

        self.repo.write("package.json", json.dumps({"version": "2.0.0", "scripts": {"lint": "y"}}))
        self.repo.commit("change lint")
        reason = self.repo.check()
        self.assertIsNotNone(reason)
        self.assertIn("package-scripts: package.json (lint)", reason)

    def test_merge_forward_that_drops_a_base_script_is_refused(self) -> None:
        self.repo.branch("feat/app")
        self.repo.write("package.json", json.dumps({"version": "1.0.1", "scripts": {"lint": "x"}}))
        self.repo.commit("branch edits package.json")
        git(self.repo.path, "checkout", "--quiet", "main")
        scripts = {"lint": "x", "lint:e2e": "playwright"}
        self.repo.write("package.json", json.dumps({"version": "1.0.0", "scripts": scripts}))
        self.repo.commit("main adds a script")
        git(self.repo.path, "push", "--quiet", "origin", "main")
        git(self.repo.path, "checkout", "--quiet", "feat/app")
        git(self.repo.path, "merge", "--quiet", "-s", "ours", "-m", "merge main", "main")

        reason = self.repo.check()

        self.assertIsNotNone(reason)
        self.assertIn("package.json (lint:e2e)", reason)

    def test_diff_is_measured_against_the_pull_request_base(self) -> None:
        self.repo.branch("feat/parent")
        self.repo.write(".circleci/config.yml", "version: 2.1\n")
        self.repo.commit("parent ci\n\nAgent-Scope: ci-config")
        git(self.repo.path, "push", "--quiet", "origin", "feat/parent")
        self.repo.branch("feat/child", "feat/parent")
        self.repo.write("src/child.ts", "export {}\n")
        self.repo.commit("child")
        self.pull_requests["feat/parent"] = {"baseRefName": "main", "body": ""}
        self.pull_requests["feat/child"] = {"baseRefName": "feat/parent", "body": ""}

        self.assertIsNone(self.repo.check())

    def test_stack_deeper_than_two_is_refused(self) -> None:
        previous = "main"
        for name in ("feat/one", "feat/two", "feat/three"):
            self.repo.branch(name, previous)
            self.repo.write(f"src/{name}.ts", "export {}\n")
            self.repo.commit(name)
            git(self.repo.path, "push", "--quiet", "origin", name)
            self.pull_requests[name] = {"baseRefName": previous, "body": ""}
            previous = name

        git(self.repo.path, "checkout", "--quiet", "feat/two")
        self.assertIsNone(self.repo.check())
        git(self.repo.path, "checkout", "--quiet", "feat/three")
        reason = self.repo.check()
        self.assertIsNotNone(reason)
        self.assertIn("stacked at least 3 pull requests above main", reason)

    def test_parses_wrapped_and_chained_push_commands(self) -> None:
        cwd = str(self.repo.path)
        cases = {
            'GH_TOKEN="$(gh auth token --user someone)" git push -u origin feat/x': ["feat/x"],
            f"cd {cwd} && git push --force-with-lease origin HEAD:refs/heads/feat/y": [
                "HEAD:refs/heads/feat/y"
            ],
            f"git -C {cwd} push": [],
            "bash -lc 'git push origin feat/z'": ["feat/z"],
        }
        for command, refspecs in cases.items():
            with self.subTest(command=command):
                pushes = hook.find_pushes(command, "/")
                self.assertEqual(len(pushes), 1)
                self.assertEqual(pushes[0].refspecs, refspecs)
        self.assertEqual(hook.find_pushes("git push origin --delete feat/x", cwd), [])
        self.assertEqual(hook.find_pushes("git push --tags", cwd), [])

    def test_deny_output_uses_the_pre_tool_use_contract(self) -> None:
        self.repo.branch("feat/app")
        self.repo.write(".circleci/config.yml", "version: 2.1\n")
        self.repo.commit("ci")
        event = json.dumps(
            {
                "tool_name": "exec_command",
                "tool_input": {"cmd": "git push origin feat/app", "workdir": str(self.repo.path)},
            }
        )
        with (
            mock.patch("sys.stdin", __import__("io").StringIO(event)),
            mock.patch("sys.stdout", new_callable=__import__("io").StringIO) as output,
        ):
            self.assertEqual(hook.main(), 0)
        decision = json.loads(output.getvalue())["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("ci-config", decision["permissionDecisionReason"])

    def test_unreadable_input_never_blocks(self) -> None:
        with mock.patch("sys.stdin", __import__("io").StringIO("not json")):
            self.assertEqual(hook.main(), 0)


if __name__ == "__main__":
    unittest.main()
