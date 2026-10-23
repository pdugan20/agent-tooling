"""Exercise setup with isolated homes and local CLI doubles, without network or installs."""

import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLI_DOUBLE = """#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
runtime = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["SETUP_CALLS"], "a") as log:
    log.write(json.dumps([runtime, *args]) + "\\n")
if runtime in ("sourcekit-lsp", "typescript-language-server"):
    sys.exit(0)
if runtime == "npm":
    assert args == ["install", "--global", "typescript", "typescript-language-server"]
    target = Path(sys.argv[0]).with_name("typescript-language-server")
    target.symlink_to(Path(sys.argv[0]).with_name("sourcekit-lsp"))
    sys.exit(0)
root = Path(os.environ["SETUP_REPOSITORY"])
if args == ["plugin", "list", "--json"]:
    ids = (root / "config" / f"{runtime}-plugins.txt").read_text().splitlines()
    state = Path(os.environ["SETUP_CALLS"]).with_name(runtime + "-added.json")
    added = json.loads(state.read_text()) if state.exists() else []
    ids = [item for item in ids if item != ids[0] or item in added]
    pin = json.loads((root / "config/superpowers.json").read_text())
    rows = [{("pluginId" if runtime == "codex" else "id"): item,
             "enabled": True, "scope": "user", "version": pin["forkVersion"]}
            for item in [*ids, "external-extra@outside", "mintlify-docs@patrick-tools"]
            if item and not item.startswith("#")]
    print(json.dumps({"installed": rows} if runtime == "codex" else rows))
elif args[:3] == ["plugin", "marketplace", "list"]:
    print("[]" if runtime == "claude" else "")
elif args[:3] == ["plugin", "marketplace", "add"]:
    pass
elif args[:3] in (["plugin", "marketplace", "upgrade"], ["plugin", "marketplace", "update"]):
    assert len(args) == 4, "Bulk marketplace refresh is forbidden"
    expected = {line.rsplit("@", 1)[1] for line in
                (root / "config" / f"{runtime}-plugins.txt").read_text().splitlines() if line}
    assert args[3] in expected
elif args[:2] == ["plugin", "update"]:
    assert args[2] in (root / "config" / f"{runtime}-plugins.txt").read_text().splitlines()
elif args[:2] in (["plugin", "add"], ["plugin", "install"]):
    assert args[2] in (root / "config" / f"{runtime}-plugins.txt").read_text().splitlines()
    state = Path(os.environ["SETUP_CALLS"]).with_name(runtime + "-added.json")
    added = json.loads(state.read_text()) if state.exists() else []
    state.write_text(json.dumps([*added, args[2]]))
    if runtime == "claude":
        settings_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
        settings = settings_home / "settings.json"
        data = json.loads(settings.read_text()) if settings.exists() else {}
        data.setdefault("enabledPlugins", {})[args[2]] = True
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(data))
else:
    raise SystemExit("Unexpected or destructive CLI call: " + repr(args))
"""


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.codex_home = self.base / "custom-codex"
        self.profile = self.base / "custom-claude"
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.calls = self.base / "calls.jsonl"
        self.env = {
            "LC_ALL": "C",
            "HOME": str(self.home),
            "CODEX_HOME": str(self.codex_home),
            "CLAUDE_CONFIG_DIR": str(self.profile),
            "PATH": str(self.bin),
            "SETUP_CALLS": str(self.calls),
            "SETUP_REPOSITORY": str(ROOT),
        }
        for name in ("bash", "python3", "git", "dirname", "mkdir", "ln", "readlink", "awk"):
            (self.bin / name).symlink_to(shutil.which(name))
        for name in ("codex", "claude", "npm", "sourcekit-lsp", "typescript-language-server"):
            path = self.bin / name
            path.write_text(CLI_DOUBLE)
            path.chmod(0o755)

    def run_script(self, name, *args, check=True):
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / name), *args],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def recorded_calls(self):
        return (
            [json.loads(line) for line in self.calls.read_text().splitlines()]
            if self.calls.exists()
            else []
        )

    def test_codex_setup_preserves_other_owners_and_never_calls_claude(self):
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text(
            'model_provider = "local-proxy"\nmodel = "anthropic/example"\n'
            '[model_providers.local-proxy]\nbase_url = "http://127.0.0.1:10100/v1"\n'
            '[mcp_servers.external]\ncommand = "external-tool"\n'
            '[hooks]\npath = "private-hook"\n'
        )
        original = tomllib.loads(config.read_text())
        self.profile.mkdir()
        settings = self.profile / "settings.json"
        settings.write_text('{"untouched": true}\n')
        skills = self.home / ".agents/skills"
        skills.mkdir(parents=True)
        retained = skills / "outside-team"
        retained.symlink_to(self.base / "external-owner")
        retired = skills / "production-hardening"
        retired.symlink_to(ROOT / ".agents/skills/production-hardening")
        cached = self.codex_home / "plugins/cache/outside/kept.txt"
        cached.parent.mkdir(parents=True)
        cached.write_text("preserved")
        ideate = (
            self.codex_home
            / "plugins/cache/openai-curated-remote/product-design/1/skills/ideate/SKILL.md"
        )
        ideate.parent.mkdir(parents=True)
        ideate.write_text("fixture")
        # Installation preserves unrelated broken links; its final doctor reports them.
        result = self.run_script("setup-new-machine.sh", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken-link", result.stdout)
        after = tomllib.loads(config.read_text())
        for key in ("model_provider", "model", "model_providers", "hooks"):
            self.assertEqual(after[key], original[key])
        self.assertEqual(after["mcp_servers"]["external"], original["mcp_servers"]["external"])
        self.assertIn(str(ideate.resolve()), [item["path"] for item in after["skills"]["config"]])
        self.assertEqual(settings.read_text(), '{"untouched": true}\n')
        self.assertEqual(list(self.profile.iterdir()), [settings])
        self.assertEqual(retained.readlink(), self.base / "external-owner")
        self.assertTrue(retired.is_symlink())
        self.assertEqual(cached.read_text(), "preserved")
        self.assertFalse((self.home / ".codex").exists())
        self.assertEqual({call[0] for call in self.recorded_calls()}, {"codex"})
        first = config.read_bytes()
        self.run_script("bootstrap.sh")
        self.assertEqual(config.read_bytes(), first)

    def test_fresh_codex_setup_does_not_create_claude_profile(self):
        # Poison the optional commands: default setup must not even probe their CLIs.
        for name in ("claude", "npm", "sourcekit-lsp", "typescript-language-server"):
            (self.bin / name).write_text("#!/bin/sh\nexit 97\n")
        self.run_script("setup-new-machine.sh")
        self.assertFalse(self.profile.exists())
        self.assertFalse((self.home / ".claude").exists())
        self.assertTrue((self.home / ".agents/skills/feature-delivery").is_symlink())

    def test_default_configuration_locations(self):
        self.env.pop("CODEX_HOME")
        self.env.pop("CLAUDE_CONFIG_DIR")
        self.run_script("setup-new-machine.sh")
        self.assertTrue((self.home / ".codex/AGENTS.md").is_symlink())
        self.assertFalse((self.home / ".claude").exists())
        self.run_script("setup-new-machine.sh", "--claude")
        self.assertTrue((self.home / ".claude/CLAUDE.md").is_symlink())
        self.assertTrue((self.home / ".claude/skills/feature-delivery").is_symlink())

    def test_missing_harness_fails_before_configuration(self):
        for runtime in ("codex", "claude"):
            (self.bin / runtime).unlink()
        for options in ((), ("--claude",)):
            result = self.run_script("setup-new-machine.sh", *options, check=False)
            self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.profile.exists())
        self.assertFalse(self.codex_home.exists())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_optional_claude_setup_preserves_codex_and_extra_plugins(self):
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text("# provider-owned contents\n")
        self.profile.mkdir()
        settings = self.profile / "settings.json"
        settings.write_text(
            json.dumps(
                {
                    "enabledPlugins": {"external-extra@outside": True},
                    "hooks": {"Stop": [{"hooks": [{"command": "private-hook"}]}]},
                }
            )
        )
        (self.bin / "codex").write_text("#!/bin/sh\nexit 97\n")
        (self.bin / "typescript-language-server").unlink()
        self.run_script("setup-new-machine.sh", "--claude")
        self.assertEqual(config.read_text(), "# provider-owned contents\n")
        after = json.loads(settings.read_text())
        self.assertTrue(after["enabledPlugins"]["external-extra@outside"])
        self.assertEqual(after["hooks"]["Stop"][0]["hooks"][0]["command"], "private-hook")
        self.assertEqual((self.profile / "CLAUDE.md").readlink(), ROOT / "global/AGENTS.md")
        self.assertTrue((self.profile / "skills/feature-delivery").is_symlink())
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / ".agents").exists())
        calls = self.recorded_calls()
        self.assertEqual({call[0] for call in calls}, {"claude", "npm"})
        self.assertEqual(sum(call[0] == "npm" for call in calls), 1)
        self.assertFalse(
            any(any(arg in ("remove", "uninstall", "disable") for arg in call) for call in calls)
        )

    def test_refresh_preserves_unselected_plugins_and_other_harness(self):
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text(
            'model_provider = "outside"\n[model_providers.outside]\nbase_url = "local"\n'
        )
        self.run_script("refresh-codex-plugins.sh")
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["model_provider"], "outside")
        self.assertFalse(self.profile.exists())
        self.assertEqual({call[0] for call in self.recorded_calls()}, {"codex"})
        codex_calls = self.recorded_calls()
        before = config.read_bytes()
        self.run_script("refresh-claude-plugins.sh")
        self.assertEqual(config.read_bytes(), before)
        claude_calls = self.recorded_calls()[len(codex_calls) :]
        self.assertEqual({call[0] for call in claude_calls}, {"claude"})
        for runtime, calls in (("codex", codex_calls), ("claude", claude_calls)):
            selected = set((ROOT / f"config/{runtime}-plugins.txt").read_text().splitlines())
            refreshed = {
                call[3]
                for call in calls
                if call[1:3] in (["plugin", "update"], ["plugin", "add"], ["plugin", "install"])
            }
            self.assertEqual(refreshed, selected)
            self.assertFalse(
                any("remove" in call or "disable" in call or "uninstall" in call for call in calls)
            )

    def test_refresh_reports_official_superpowers_conflict_without_changing_settings(self):
        self.profile.mkdir()
        settings = self.profile / "settings.json"
        settings.write_text('{"enabledPlugins":{"superpowers@claude-plugins-official":true}}')
        before = settings.read_bytes()
        result = self.run_script("refresh-claude-plugins.sh", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Existing settings were preserved", result.stderr)
        self.assertEqual(settings.read_bytes(), before)
        self.assertEqual(self.recorded_calls(), [])
        self.assertFalse(
            any("disable" in call or "uninstall" in call for call in self.recorded_calls())
        )

    def test_conflicting_selected_link_is_preserved(self):
        skills = self.home / ".agents/skills"
        skills.mkdir(parents=True)
        name = next(
            path.name
            for path in (ROOT / ".agents/skills").iterdir()
            if (path / "SKILL.md").is_file()
        )
        target = skills / name
        target.mkdir()
        (target / "SKILL.md").write_text("local work")
        result = self.run_script("bootstrap.sh", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to replace", result.stderr)
        self.assertEqual((target / "SKILL.md").read_text(), "local work")

    def test_invalid_options_fail_before_writes_or_commands(self):
        for script in ("bootstrap.sh", "setup-new-machine.sh", "verify-setup.sh"):
            result = self.run_script(script, "--unknown", check=False)
            self.assertEqual(result.returncode, 2)
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertFalse(self.calls.exists())
        self.assertFalse(self.profile.exists())
        self.assertFalse(self.codex_home.exists())


if __name__ == "__main__":
    unittest.main()
