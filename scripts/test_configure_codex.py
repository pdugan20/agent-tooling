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


if __name__ == "__main__":
    unittest.main()
