from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate_catalog


class CatalogGenerationTests(unittest.TestCase):
    def test_catalog_contains_canonical_skills_and_plugins(self) -> None:
        catalog = generate_catalog.build_catalog()
        items = catalog["items"]

        self.assertEqual(len([item for item in items if item["type"] == "skill"]), 22)
        self.assertEqual(len([item for item in items if item["type"] == "plugin"]), 24)
        self.assertEqual(len({item["id"] for item in items}), len(items))
        self.assertEqual({item["availability"] for item in items}, {"Global"})
        self.assertEqual(catalog["schemaVersion"], 4)
        self.assertEqual(
            next(item for item in items if item["name"] == "xcodebuildmcp")["displayName"],
            "XcodeBuildMCP",
        )

    def test_custom_invocation_policy_is_visible(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        managed = {
            item["name"]: item["invocation"]
            for item in items
            if item["type"] == "skill" and item["sourceLabel"] == "Pat Dugan"
        }

        self.assertEqual(managed["feature-delivery"], "Automatic")
        self.assertEqual(managed["bootstrap-repository"], "Automatic")
        self.assertEqual(
            set(managed),
            {
                "align-ui-to-design-system",
                "analyze-ui-video",
                "audit-design-system-health",
                "bootstrap-repository",
                "code-native-ui-ideation",
                "feature-delivery",
                "feature-spike",
                "generate-mintlify-reference",
                "integrate-app-intents",
                "review-mintlify-docs",
                "scaffold-mintlify-site",
                "tune-mobile-client-performance",
                "write-mintlify-changelog",
            },
        )
        self.assertTrue(
            all(
                item["path"].startswith(".agents/skills/")
                and item["sourceUrl"].startswith("https://github.com/pdugan20/skills/blob/v3.2.0/")
                for item in items
                if item["type"] == "skill" and item["name"] in managed
            )
        )

    def test_upstream_skills_keep_their_provenance(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        upstream = {
            item["name"]: (item["sourceLabel"], item["path"], item["sourceUrl"])
            for item in items
            if item["type"] == "skill" and item["source"] == "third-party"
        }

        self.assertEqual(
            upstream,
            {
                "animation-vocabulary": (
                    "Emil Kowalski",
                    ".agents/skills/animation-vocabulary/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/animation-vocabulary/SKILL.md",
                ),
                "apple-design": (
                    "Emil Kowalski",
                    ".agents/skills/apple-design/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md",
                ),
                "emil-design-eng": (
                    "Emil Kowalski",
                    ".agents/skills/emil-design-eng/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/emil-design-eng/SKILL.md",
                ),
                "find-animation-opportunities": (
                    "Emil Kowalski",
                    ".agents/skills/find-animation-opportunities/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/find-animation-opportunities/SKILL.md",
                ),
                "pick-ui-library": (
                    "Emil Kowalski",
                    ".agents/skills/pick-ui-library/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md",
                ),
                "review-animations": (
                    "Emil Kowalski",
                    ".agents/skills/review-animations/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/review-animations/SKILL.md",
                ),
                "find-skills": (
                    "Vercel Labs",
                    ".agents/skills/find-skills/SKILL.md",
                    "https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md",
                ),
                "swiftui-pro": (
                    "Paul Hudson",
                    ".agents/skills/swiftui-pro/SKILL.md",
                    "https://github.com/twostraws/swiftui-agent-skill/blob/main/swiftui-pro/SKILL.md",
                ),
                "xcodebuildmcp": (
                    "Sentry",
                    ".agents/skills/xcodebuildmcp/SKILL.md",
                    "https://github.com/getsentry/XcodeBuildMCP/blob/v2.7.0/skills/xcodebuildmcp/SKILL.md",
                ),
            },
        )

    def test_superpowers_plugin_provenance_is_explicit(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        plugins = [
            item
            for item in items
            if "superpowers@superpowers-configured" in item.get("pluginIds", [])
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

    def test_mintlify_docs_are_personal_skills(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        plugin_ids = {
            plugin_id
            for item in items
            if item["type"] == "plugin"
            for plugin_id in item.get("pluginIds", [])
        }
        personal_skills = {
            item["name"]
            for item in items
            if item["type"] == "skill" and item["sourceLabel"] == "Pat Dugan"
        }

        self.assertNotIn("mintlify-docs@patrick-plugins", plugin_ids)
        self.assertTrue(
            {
                "generate-mintlify-reference",
                "review-mintlify-docs",
                "scaffold-mintlify-site",
                "write-mintlify-changelog",
            }
            <= personal_skills
        )
        self.assertIn("mintlify@mintlify-marketplace", plugin_ids)

    def test_codex_managed_plugins_are_separate_from_cli_plugins(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        managed = {
            installation["pluginId"]
            for item in items
            if item["type"] == "plugin"
            for installation in item["installations"]
            if installation["delivery"] == "managed"
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
                installation["runtime"] == "codex" and installation["delivery"] == "managed"
                for item in items
                if item["type"] == "plugin"
                for installation in item["installations"]
                if installation["pluginId"] in managed
            )
        )

    def test_agent_specific_plugin_ids_merge_into_logical_capabilities(self) -> None:
        plugins = {
            item["name"]: item
            for item in generate_catalog.build_catalog()["items"]
            if item["type"] == "plugin"
        }

        for name in ("cloudflare", "figma", "firebase", "github", "vercel"):
            self.assertEqual(plugins[name]["runtimes"], ["codex", "claude"])
            self.assertEqual(len(plugins[name]["installations"]), 2)
        self.assertEqual(
            {item["pluginId"] for item in plugins["figma"]["installations"]},
            {
                "figma@openai-curated-remote",
                "figma@claude-plugins-official",
            },
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
                "description: >\n"
                "  Example project workflow shared by both\n"
                "  supported agents.\n"
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
        self.assertEqual(
            items[0]["description"],
            "Example project workflow shared by both supported agents.",
        )
        self.assertEqual(items[0]["repository"], "example-app")
        self.assertEqual(items[0]["runtimes"], ["codex", "claude"])
        self.assertEqual(items[0]["source"], "repository")
        self.assertIsNone(items[0]["pathHref"])
        self.assertIsNone(items[0]["sourceUrl"])

    def test_humanizes_use_railway_without_an_acronym(self) -> None:
        self.assertEqual(generate_catalog.humanize_name("use-railway"), "Use Railway")

    def test_project_snapshot_links_locked_skills_to_their_upstream_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repos_root = Path(temporary)
            repository = repos_root / "example-app"
            (repository / ".git").mkdir(parents=True)
            skill_root = repository / ".agents/skills/apple-design"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                "---\nname: apple-design\ndescription: Apple design reference.\n---\n",
                encoding="utf-8",
            )
            (repository / "skills-lock.json").write_text(
                '{"version":1,"skills":{"apple-design":'
                '{"source":"emilkowalski/skills","sourceType":"github",'
                '"skillPath":"skills/apple-design/SKILL.md"}}}',
                encoding="utf-8",
            )

            items = generate_catalog.project_skill_items(repos_root)

        self.assertEqual(items[0]["sourceLabel"], "Emil Kowalski")
        self.assertEqual(
            items[0]["sourceUrl"],
            "https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md",
        )


if __name__ == "__main__":
    unittest.main()
