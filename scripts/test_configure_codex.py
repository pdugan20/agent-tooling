from __future__ import annotations

import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("configure-codex.py")
SPEC = importlib.util.spec_from_file_location("configure_codex", SCRIPT)
assert SPEC and SPEC.loader
configure_codex = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(configure_codex)


class ConfigureCodexTests(unittest.TestCase):
    MANAGED_MCP_SERVERS = {
        "xcodebuildmcp": {
            "command": "npx",
            "args": ["--yes", "xcodebuildmcp@2.7.0", "mcp"],
            "enabled": True,
            "env": {
                "XCODEBUILDMCP_ENABLED_WORKFLOWS": "simulator,ui-automation,debugging",
                "XCODEBUILDMCP_SENTRY_DISABLED": "true",
            },
            "startup_timeout_sec": 120,
            "tool_timeout_sec": 300,
        }
    }

    def test_disables_product_design_router_and_image_ideation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            skills = (
                home / ".codex/plugins/cache/openai-curated-remote/product-design/0.1.52/skills"
            )
            for name in ("ideate", "index"):
                skill = skills / name / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(f"---\nname: {name}\n---\n")

            original = 'model = "test"\n'
            updated = configure_codex.update_config(original, home)
            parsed = tomllib.loads(updated)

            disabled = {
                item["path"] for item in parsed["skills"]["config"] if item["enabled"] is False
            }
            expected = {str((skills / name / "SKILL.md").resolve()) for name in ("ideate", "index")}
            self.assertEqual(disabled, expected)
            self.assertEqual(configure_codex.update_config(updated, home), updated)

    def test_changes_existing_matching_override_to_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            skill = home / ".codex/.tmp/plugins/plugins/product-design/skills/ideate/SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text("---\nname: ideate\n---\n")
            original = (
                'project_doc_fallback_filenames = ["CLAUDE.md"]\n\n'
                "[[skills.config]]\n"
                f'path = "{skill.resolve()}"\n'
                "enabled = true\n"
            )

            updated = configure_codex.update_config(original, home)
            parsed = tomllib.loads(updated)

            self.assertFalse(parsed["skills"]["config"][0]["enabled"])

    def test_computer_use_repair_stays_in_selected_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            custom = home / "custom-codex"
            for selected in (home / ".codex", custom):
                client = selected / configure_codex.COMPUTER_USE_SUFFIX
                client.parent.mkdir(parents=True)
                client.write_text("#!/bin/sh\nexit 0\n")
                client.chmod(0o755)
            original = (
                "[mcp_servers.computer-use]\n"
                f'command = "{configure_codex.RELATIVE_COMPUTER_USE_COMMAND}"\n'
            )
            updated = configure_codex.update_config(original, home, codex_home=custom)
            parsed = tomllib.loads(updated)
            self.assertEqual(
                parsed["mcp_servers"]["computer-use"]["command"],
                str(custom / configure_codex.COMPUTER_USE_SUFFIX),
            )
            (custom / configure_codex.COMPUTER_USE_SUFFIX).unlink()
            updated = configure_codex.update_config(original, home, codex_home=custom)
            self.assertEqual(
                tomllib.loads(updated)["mcp_servers"]["computer-use"]["command"],
                configure_codex.RELATIVE_COMPUTER_USE_COMMAND,
            )

    def test_disables_an_additional_repository_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            nested_skill = home / "repo/.agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"
            nested_skill.parent.mkdir(parents=True)
            nested_skill.write_text("---\nname: swiftui-pro\n---\n")

            updated = configure_codex.update_config("", home, (nested_skill,))
            parsed = tomllib.loads(updated)

            self.assertEqual(
                parsed["skills"]["config"],
                [{"path": str(nested_skill.resolve()), "enabled": False}],
            )

    def test_adds_pinned_managed_mcp_server_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = 'model = "test"\n'

            updated = configure_codex.update_config(
                original,
                home,
                managed_mcp_servers=self.MANAGED_MCP_SERVERS,
            )
            parsed = tomllib.loads(updated)

            self.assertEqual(
                parsed["mcp_servers"]["xcodebuildmcp"],
                self.MANAGED_MCP_SERVERS["xcodebuildmcp"],
            )
            self.assertEqual(
                configure_codex.update_config(
                    updated,
                    home,
                    managed_mcp_servers=self.MANAGED_MCP_SERVERS,
                ),
                updated,
            )

    def test_replaces_stale_managed_mcp_server_without_touching_neighbors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = (
                "[mcp_servers.xcodebuildmcp]\n"
                'command = "npx"\n'
                'args = ["--yes", "xcodebuildmcp@latest", "mcp"]\n\n'
                "[mcp_servers.other]\n"
                'command = "other-server"\n'
            )

            updated = configure_codex.update_config(
                original,
                home,
                managed_mcp_servers=self.MANAGED_MCP_SERVERS,
            )
            parsed = tomllib.loads(updated)

            self.assertEqual(parsed["mcp_servers"]["other"]["command"], "other-server")
            self.assertEqual(
                parsed["mcp_servers"]["xcodebuildmcp"],
                self.MANAGED_MCP_SERVERS["xcodebuildmcp"],
            )

    def test_replaces_managed_mcp_server_without_consuming_array_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = (
                "[mcp_servers.xcodebuildmcp]\n"
                'command = "npx"\n'
                'args = ["--yes", "xcodebuildmcp@latest", "mcp"]\n\n'
                "[[skills.config]]\n"
                'path = "/tmp/example/SKILL.md"\n'
                "enabled = false\n"
            )

            updated = configure_codex.update_config(
                original,
                home,
                managed_mcp_servers=self.MANAGED_MCP_SERVERS,
            )
            parsed = tomllib.loads(updated)

            self.assertEqual(
                parsed["skills"]["config"],
                [{"path": "/tmp/example/SKILL.md", "enabled": False}],
            )

    def test_push_scope_hook_is_added_once_beside_existing_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = (
                "[hooks.state]\n\n"
                "[[hooks.PreToolUse]]\n"
                'matcher = "^Bash$"\n\n'
                "[[hooks.PreToolUse.hooks]]\n"
                'type = "command"\n'
                'command = "/usr/bin/python3 /private/branch-naming/validate.py"\n\n'
                "[[skills.config]]\n"
                'path = "/tmp/example/SKILL.md"\n'
                "enabled = false\n"
            )
            old = Path("/old checkout/global/hooks/agent_push_scope.py")
            new = Path("/new/global/hooks/agent_push_scope.py")

            first = configure_codex.update_config(original, home, push_scope_hook=old)
            moved = configure_codex.update_config(first, home, push_scope_hook=new)
            again = configure_codex.update_config(moved, home, push_scope_hook=new)

            self.assertEqual(again, moved)
            parsed = tomllib.loads(moved)
            entries = parsed["hooks"]["PreToolUse"]
            self.assertEqual(len(entries), 2)
            self.assertIn("branch-naming", entries[0]["hooks"][0]["command"])
            self.assertEqual(entries[1]["hooks"][0]["command"], f"python3 {new}")
            self.assertEqual(entries[1]["hooks"][0]["timeout"], 30)
            self.assertRegex("exec_command", entries[1]["matcher"])
            self.assertRegex("functions.exec_command", entries[1]["matcher"])
            self.assertEqual(len(parsed["skills"]["config"]), 1)

    def test_push_scope_hook_update_keeps_sibling_commands_in_its_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            first = configure_codex.update_config(
                "", home, push_scope_hook=Path("/old/agent_push_scope.py")
            )
            shared = first + (
                '\n[[hooks.PreToolUse.hooks]]\ntype = "command"\ncommand = "echo mine"\n'
            )

            updated = configure_codex.update_config(
                shared, home, push_scope_hook=Path("/new/agent_push_scope.py")
            )

            entry = tomllib.loads(updated)["hooks"]["PreToolUse"][0]
            commands = [hook["command"] for hook in entry["hooks"]]
            self.assertEqual(commands, ["python3 /new/agent_push_scope.py", "echo mine"])
            self.assertEqual(entry["hooks"][0]["timeout"], 30)

    def test_push_scope_hook_is_optional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            updated = configure_codex.update_config("", Path(directory))
            self.assertNotIn("agent_push_scope", updated)
            self.assertTrue(configure_codex.PUSH_SCOPE_HOOK.is_file())

    def test_renders_tool_allowlist_and_replaces_an_unrestricted_server(self) -> None:
        servers = {
            "circleci": {
                "command": "/opt/homebrew/bin/circleci",
                "args": ["mcp", "start"],
                "enabled": True,
                "enabled_tools": ["circleci_job_get", "circleci_job_output"],
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = (
                "[mcp_servers.circleci]\n"
                'command = "/opt/homebrew/bin/circleci"\n'
                'args = ["mcp", "start"]\n'
            )

            updated = configure_codex.update_config(original, home, managed_mcp_servers=servers)

            self.assertEqual(tomllib.loads(updated)["mcp_servers"]["circleci"], servers["circleci"])
            self.assertEqual(
                configure_codex.update_config(updated, home, managed_mcp_servers=servers),
                updated,
            )

    def test_rejects_invalid_tool_allowlists(self) -> None:
        base = {"command": "server", "args": []}
        for tools in ([], ["dup", "dup"], ["bad name"], "circleci_job_get"):
            with self.subTest(tools=tools), self.assertRaises(ValueError):
                configure_codex.update_config(
                    "",
                    Path("/tmp"),
                    managed_mcp_servers={"server": {**base, "enabled_tools": tools}},
                )


if __name__ == "__main__":
    unittest.main()
