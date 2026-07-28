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
        custom = {
            item["name"]: item["invocation"]
            for item in items
            if item["sourceLabel"] == "Built here"
        }

        self.assertEqual(custom["feature-delivery"], "Automatic")
        self.assertEqual(custom["production-hardening"], "Explicit")

    def test_superpowers_plugin_provenance_is_explicit(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        plugins = [
            item for item in items if item.get("pluginId") == "superpowers@superpowers-configured"
        ]

        self.assertEqual(
            {tuple(plugin["runtimes"]) for plugin in plugins}, {("codex",), ("claude",)}
        )
        self.assertTrue(
            all(plugin["displayName"] == "Superpowers (Configured)" for plugin in plugins)
        )
        self.assertTrue(all("upstream" in plugin["description"].lower() for plugin in plugins))
        self.assertTrue(all(plugin["path"] == "config/superpowers.json" for plugin in plugins))
        self.assertTrue(all(plugin["version"] == "6.2.0-config.2" for plugin in plugins))
        self.assertNotIn("Desired", {item["state"] for item in items})


if __name__ == "__main__":
    unittest.main()
