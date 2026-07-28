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


if __name__ == "__main__":
    unittest.main()
