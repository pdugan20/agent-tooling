from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("configure-claude.py")
SPEC = importlib.util.spec_from_file_location("configure_claude", MODULE_PATH)
assert SPEC and SPEC.loader
configure_claude = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(configure_claude)


class ConfigureClaudeTests(unittest.TestCase):
    def test_routes_superpowers_to_configured_fork(self) -> None:
        data = {
            "enabledPlugins": {"unrelated@example": True},
            "skillOverrides": {
                "production-hardening": "user-invocable-only",
                "strict-tdd": "user-invocable-only",
                "unrelated-skill": "name-only",
            },
        }

        updated = configure_claude.update_settings(data)

        self.assertIs(updated["enabledPlugins"]["unrelated@example"], True)
        self.assertIs(updated["enabledPlugins"]["superpowers@claude-plugins-official"], False)
        self.assertIs(updated["enabledPlugins"]["superpowers@superpowers-configured"], True)
        self.assertNotIn("strict-tdd", updated["skillOverrides"])
        self.assertNotIn("production-hardening", updated["skillOverrides"])
        self.assertEqual(updated["skillOverrides"]["unrelated-skill"], "name-only")

    def test_output_style_is_selected(self) -> None:
        self.assertEqual(configure_claude.update_settings({})["outputStyle"], "simple-english")

    def test_output_style_replaces_a_previous_choice(self) -> None:
        # The style is managed, not merely defaulted: a stale value from an earlier
        # release must not survive, or a machine keeps writing in the old style.
        data = {"outputStyle": "explanatory"}

        self.assertEqual(configure_claude.update_settings(data)["outputStyle"], "simple-english")

    def test_agents_md_hook_is_installed_once_and_preserves_other_hooks(self) -> None:
        hook = Path("/checkout/global/hooks/agents_md_context.py")
        stale = "python3 /old/checkout/global/hooks/agents_md_context.py"
        data = {
            "hooks": {
                "Stop": [{"hooks": [{"type": "command", "command": "python3 /x/stop_check.py"}]}],
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "echo unrelated"}]},
                    {"hooks": [{"type": "command", "command": stale}]},
                ],
            }
        }

        configure_claude.update_settings(data, hook)
        updated = configure_claude.update_settings(data, hook)

        session_start = updated["hooks"]["SessionStart"]
        commands = [entry["command"] for group in session_start for entry in group["hooks"]]
        self.assertEqual(commands, ["echo unrelated", f"python3 {hook}"])
        self.assertEqual(session_start[-1]["matcher"], "startup|clear|compact")
        self.assertIn("Stop", updated["hooks"])

    def test_agents_md_hook_command_quotes_paths_with_spaces(self) -> None:
        hook = Path("/Users/me/Mobile Documents/agent-tooling/global/hooks/agents_md_context.py")

        updated = configure_claude.update_settings({}, hook)

        command = updated["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertEqual(command, f"python3 '{hook}'")

    def test_default_agents_md_hook_points_at_this_checkout(self) -> None:
        self.assertTrue(configure_claude.AGENTS_MD_HOOK.is_file())


if __name__ == "__main__":
    unittest.main()
