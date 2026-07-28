from __future__ import annotations

import unittest

import generate_catalog


class CatalogGenerationTests(unittest.TestCase):
    def test_catalog_contains_canonical_skills_and_plugins(self) -> None:
        catalog = generate_catalog.build_catalog()
        items = catalog["items"]

        self.assertEqual(len([item for item in items if item["type"] == "skill"]), 8)
        self.assertEqual(len([item for item in items if item["type"] == "plugin"]), 20)
        self.assertEqual(len({item["id"] for item in items}), len(items))

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


if __name__ == "__main__":
    unittest.main()
