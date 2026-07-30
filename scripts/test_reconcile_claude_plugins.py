from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import reconcile_claude_plugins


class ReconcileClaudePluginsTests(unittest.TestCase):
    def test_manifest_ignores_comments_and_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "plugins.txt"
            manifest.write_text(
                "# Shared plugins\n\nfigma@claude-plugins-official\n",
                encoding="utf-8",
            )

            self.assertEqual(
                reconcile_claude_plugins.desired_plugin_ids(manifest),
                {"figma@claude-plugins-official"},
            )

    def test_only_enabled_undeclared_user_plugins_are_returned(self) -> None:
        plugins = [
            {
                "id": "figma@claude-plugins-official",
                "scope": "user",
                "enabled": True,
            },
            {"id": "extra@marketplace", "scope": "user", "enabled": True},
            {"id": "off@marketplace", "scope": "user", "enabled": False},
            {"id": "project@marketplace", "scope": "project", "enabled": True},
            {"id": "local-skill@skills-dir", "scope": "user", "enabled": True},
        ]

        self.assertEqual(
            reconcile_claude_plugins.undeclared_enabled_plugins(
                plugins, {"figma@claude-plugins-official"}
            ),
            ["extra@marketplace"],
        )


if __name__ == "__main__":
    unittest.main()
