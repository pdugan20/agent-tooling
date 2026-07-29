from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate_catalog


class CatalogGenerationTests(unittest.TestCase):
    def test_catalog_contains_canonical_skills_and_plugins(self) -> None:
        catalog = generate_catalog.build_catalog()
        items = catalog["items"]

        self.assertEqual(len([item for item in items if item["type"] == "skill"]), 10)
        self.assertEqual(len([item for item in items if item["type"] == "plugin"]), 23)
        self.assertEqual(len({item["id"] for item in items}), len(items))
        self.assertEqual({item["availability"] for item in items}, {"Global"})
        self.assertEqual(catalog["schemaVersion"], 2)

    def test_custom_invocation_policy_is_visible(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        managed = {
            item["name"]: item["invocation"]
            for item in items
            if item["sourceLabel"] == "Managed here"
        }

        self.assertEqual(managed["feature-delivery"], "Automatic")
        self.assertEqual(managed["production-hardening"], "Explicit")
        self.assertEqual(
            set(managed),
            {
                "code-native-ui-ideation",
                "feature-delivery",
                "production-hardening",
            },
        )

    def test_upstream_skills_keep_their_provenance(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        upstream = {
            item["name"]: (item["sourceLabel"], item["path"])
            for item in items
            if item["type"] == "skill" and item["source"] == "third-party"
        }

        self.assertEqual(
            upstream,
            {
                "animation-vocabulary": (
                    "Emil Kowalski",
                    ".agents/skills/animation-vocabulary/SKILL.md",
                ),
                "apple-design": (
                    "Emil Kowalski",
                    ".agents/skills/apple-design/SKILL.md",
                ),
                "emil-design-eng": (
                    "Emil Kowalski",
                    ".agents/skills/emil-design-eng/SKILL.md",
                ),
                "find-animation-opportunities": (
                    "Emil Kowalski",
                    ".agents/skills/find-animation-opportunities/SKILL.md",
                ),
                "pick-ui-library": (
                    "Emil Kowalski",
                    ".agents/skills/pick-ui-library/SKILL.md",
                ),
                "review-animations": (
                    "Emil Kowalski",
                    ".agents/skills/review-animations/SKILL.md",
                ),
                "swiftui-pro": (
                    "Paul Hudson",
                    ".agents/skills/swiftui-pro/SKILL.md",
                ),
            },
        )

    def test_superpowers_plugin_provenance_is_explicit(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        plugins = [
            item for item in items if item.get("pluginId") == "superpowers@superpowers-configured"
        ]

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["runtimes"], ["codex", "claude"])
        self.assertTrue(
            all(plugin["displayName"] == "Superpowers (Configured)" for plugin in plugins)
        )
        self.assertTrue(all("upstream" in plugin["description"].lower() for plugin in plugins))
        self.assertTrue(all(plugin["path"] == "config/superpowers.json" for plugin in plugins))
        self.assertTrue(all(plugin["version"] == "6.2.0-config.2" for plugin in plugins))
        self.assertNotIn("Desired", {item["state"] for item in items})

    def test_mintlify_docs_is_one_cross_runtime_plugin(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        plugins = [
            item for item in items if item.get("pluginId") == "mintlify-docs@pdugan20-plugins"
        ]

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["runtimes"], ["codex", "claude"])
        self.assertEqual(plugins[0]["sourceLabel"], "Pat Dugan")

    def test_codex_managed_plugins_are_separate_from_cli_plugins(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        managed = {
            item["pluginId"]
            for item in items
            if item["type"] == "plugin" and item["state"] == "Managed by Codex"
        }

        self.assertEqual(
            managed,
            {
                "data-analytics@openai-curated-remote",
                "figma@openai-curated-remote",
                "github@openai-curated-remote",
                "openai-developers@openai-curated-remote",
                "product-design@openai-curated-remote",
                "slack@openai-curated-remote",
                "vercel@openai-curated-remote",
            },
        )
        self.assertTrue(
            all(
                item["sourceLabel"] == "Managed by Codex"
                for item in items
                if item.get("pluginId") in managed
            )
        )

    def test_project_snapshot_discovers_shared_repository_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repos_root = Path(temporary)
            repository = repos_root / "example-app"
            (repository / ".git").mkdir(parents=True)
            skill_root = repository / ".agents/skills/example-skill"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                "---\n"
                "name: example-skill\n"
                "description: Example project workflow.\n"
                "---\n\n"
                "# Example\n",
                encoding="utf-8",
            )
            claude_skills = repository / ".claude/skills"
            claude_skills.mkdir(parents=True)
            (claude_skills / "example-skill").symlink_to(Path("../../.agents/skills/example-skill"))

            items = generate_catalog.project_skill_items(repos_root)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["availability"], "Project")
        self.assertEqual(items[0]["repository"], "example-app")
        self.assertEqual(items[0]["runtimes"], ["codex", "claude"])
        self.assertEqual(items[0]["source"], "repository")
        self.assertIsNone(items[0]["pathHref"])


if __name__ == "__main__":
    unittest.main()
