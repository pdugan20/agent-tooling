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


if __name__ == "__main__":
    unittest.main()
