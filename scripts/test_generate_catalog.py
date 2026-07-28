from __future__ import annotations

import unittest

import generate_catalog


class CatalogGenerationTests(unittest.TestCase):
    def test_catalog_contains_canonical_skills_and_plugins(self) -> None:
        catalog = generate_catalog.build_catalog()
        items = catalog["items"]

        self.assertEqual(len([item for item in items if item["type"] == "skill"]), 12)
        self.assertEqual(len([item for item in items if item["type"] == "plugin"]), 19)
        self.assertEqual(len({item["id"] for item in items}), len(items))

    def test_delivery_invocation_policy_is_visible(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        delivery = {
            item["name"]: item["invocation"]
            for item in items
            if item["sourceLabel"] == "Patrick Delivery"
        }

        self.assertEqual(delivery["feature-delivery"], "Automatic")
        self.assertEqual(delivery["strict-tdd"], "Explicit")


if __name__ == "__main__":
    unittest.main()
