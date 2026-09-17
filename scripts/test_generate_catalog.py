from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate_catalog


class CatalogGenerationTests(unittest.TestCase):
    def test_catalog_contains_canonical_skills_and_plugins(self) -> None:
        catalog = generate_catalog.build_catalog()
        items = catalog["items"]

        self.assertEqual(len([item for item in items if item["type"] == "skill"]), 27)
        self.assertEqual(len([item for item in items if item["type"] == "plugin"]), 24)
        self.assertEqual(len({item["id"] for item in items}), len(items))
        self.assertEqual({item["availability"] for item in items}, {"Global"})
        self.assertEqual(catalog["schemaVersion"], 5)
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

    def test_skills_expose_repository_directory_and_owner_identity(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        feature_delivery = next(item for item in items if item["id"] == "skill:feature-delivery")

        self.assertEqual(
            feature_delivery["repositoryUrl"],
            "https://github.com/pdugan20/skills",
        )
        self.assertEqual(
            feature_delivery["skillsShUrl"],
            "https://skills.sh/pdugan20/skills/feature-delivery",
        )
        self.assertEqual(
            feature_delivery["ownerAvatarUrl"],
            "https://github.com/pdugan20.png?size=96",
        )
        self.assertIsNone(feature_delivery["brand"])

    def test_official_plugins_use_product_identity(self) -> None:
        items = generate_catalog.build_catalog()["items"]
        anthropic = next(item for item in items if item["name"] == "claude-code-setup")
        openai = next(item for item in items if item["name"] == "data-analytics")

        self.assertEqual(anthropic["brand"], "claudecode")
        self.assertEqual(
            anthropic["repositoryUrl"],
            "https://github.com/anthropics/claude-plugins-official",
        )
        self.assertEqual(openai["brand"], "openai")
        self.assertIsNone(openai["repositoryUrl"])

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
                "shadcn": (
                    "shadcn/ui",
                    ".agents/skills/shadcn/SKILL.md",
                    "https://github.com/shadcn-ui/ui/blob/7c9eaba1c0a6404c990c144a654792e3313c650d/skills/shadcn/SKILL.md",
                ),
                "accessibility": (
                    "Addy Osmani",
                    ".agents/skills/accessibility/SKILL.md",
                    "https://github.com/addyosmani/web-quality-skills/blob/main/skills/accessibility/SKILL.md",
                ),
                "vercel-composition-patterns": (
                    "Vercel Labs",
                    ".agents/skills/vercel-composition-patterns/SKILL.md",
                    "https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/skills/composition-patterns/SKILL.md",
                ),
                "playwright-best-practices": (
                    "Currents",
                    ".agents/skills/playwright-best-practices/SKILL.md",
                    "https://github.com/currents-dev/playwright-best-practices-skill/blob/main/playwright-best-practices/SKILL.md",
                ),
                "animate-expo": (
                    "Emil Kowalski",
                    ".agents/skills/animate-expo/SKILL.md",
                    "https://github.com/emilkowalski/skills/blob/main/skills/animate-expo/SKILL.md",
                ),
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
                    "https://github.com/vercel-labs/skills/blob/d6b37f62ae23c3825b0ed16c73e123eee0a41fdc/skills/find-skills/SKILL.md",
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
        mintlify_plugin = next(
            item for item in items if "mintlify@mintlify-marketplace" in item.get("pluginIds", [])
        )
        self.assertEqual(mintlify_plugin["displayName"], "Mintlify Official Plugin")
        self.assertEqual(mintlify_plugin["sourceLabel"], "Mintlify")

    def test_runtime_owned_plugins_have_a_human_source_label(self) -> None:
        metadata: dict[str, object] = {}

        self.assertEqual(
            generate_catalog.source_details("browser@openai-bundled", metadata),
            ("openai", "Built into Codex"),
        )
        self.assertEqual(
            generate_catalog.source_details("pdf@openai-primary-runtime", metadata),
            ("openai", "Built into Codex"),
        )
        self.assertIn(
            "codex-app-tools@openai-bundled",
            generate_catalog.HIDDEN_RUNTIME_PLUGIN_IDS,
        )

    def test_runtime_snapshot_hides_plumbing_and_disabled_tombstones(self) -> None:
        self.assertFalse(
            generate_catalog.include_runtime_plugin(
                "codex-app-tools@openai-bundled",
                enabled=True,
                desired=None,
            )
        )
        self.assertFalse(
            generate_catalog.include_runtime_plugin(
                "mintlify@claude-plugins-official",
                enabled=False,
                desired=None,
            )
        )
        self.assertFalse(
            generate_catalog.include_runtime_plugin(
                "browser@openai-bundled",
                enabled=True,
                desired=None,
            )
        )
        self.assertFalse(
            generate_catalog.include_runtime_plugin(
                "documents@openai-primary-runtime",
                enabled=True,
                desired=None,
            )
        )
        self.assertTrue(
            generate_catalog.include_runtime_plugin(
                "expected@example",
                enabled=False,
                desired={"id": "plugin:expected"},
            )
        )
        self.assertTrue(
            generate_catalog.include_runtime_plugin(
                "unexpected@example",
                enabled=True,
                desired=None,
            )
        )

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
        self.assertIsNone(items[0]["repositoryUrl"])
        self.assertIsNone(items[0]["skillsShUrl"])

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
        self.assertEqual(
            items[0]["repositoryUrl"],
            "https://github.com/emilkowalski/skills",
        )
        self.assertEqual(
            items[0]["skillsShUrl"],
            "https://skills.sh/emilkowalski/skills/apple-design",
        )


if __name__ == "__main__":
    unittest.main()
