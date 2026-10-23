#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
runtime=codex
if (($#)); then
  if [[ $# == 1 && $1 == --claude ]]; then
    runtime=claude
  else
    echo "Usage: $0 [--claude]" >&2
    exit 2
  fi
fi

claude_config_dir=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}
codex_home=${CODEX_HOME:-"$HOME/.codex"}
failures=0
superpowers_plugin_id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["pluginId"])' "$ROOT/config/superpowers.json")
superpowers_version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["forkVersion"])' "$ROOT/config/superpowers.json")

pass() {
  echo "PASS $1"
}

fail() {
  echo "FAIL $1" >&2
  failures=$((failures + 1))
}

check_command() {
  local command_name=$1
  local install_hint=$2
  if command -v "$command_name" >/dev/null 2>&1; then
    pass "$command_name is available for Claude's LSP plugin"
  else
    fail "$command_name is missing; $install_hint"
  fi
}

check_link() {
  local source=$1
  local target=$2
  if [[ -L $target && $(readlink "$target") == "$source" ]]; then
    pass "$target"
  else
    fail "$target should link to $source"
  fi
}

if [[ $runtime == claude ]]; then
  check_link "$ROOT/global/AGENTS.md" "$claude_config_dir/CLAUDE.md"
  check_command sourcekit-lsp "install Xcode or the Swift toolchain"
  check_command typescript-language-server "run npm install --global typescript typescript-language-server"
  skills_target="$claude_config_dir/skills"
else
  check_link "$ROOT/global/AGENTS.md" "$codex_home/AGENTS.md"
  skills_target="$HOME/.agents/skills"
fi

for skill_dir in "$ROOT"/.agents/skills/*; do
  [[ -f $skill_dir/SKILL.md ]] || continue
  check_link "$skill_dir" "$skills_target/${skill_dir##*/}"
done

if ! command -v "$runtime" >/dev/null 2>&1; then
  fail "$runtime CLI is not installed"
  exit 1
fi

if [[ $runtime == codex ]]; then
  if python3 - "$codex_home/config.toml" "$ROOT/config/codex-mcp-servers.json" <<'PY'; then
import json
import sys
import tomllib
from pathlib import Path

config = tomllib.loads(Path(sys.argv[1]).read_text())
expected = json.loads(Path(sys.argv[2]).read_text())
actual = config.get("mcp_servers", {})
raise SystemExit(0 if all(actual.get(name) == spec for name, spec in expected.items()) else 1)
PY
    pass "Managed Codex MCP servers match the pinned manifest"
  else
    fail "Managed Codex MCP servers drifted; rerun bootstrap"
  fi

  codex_plugins=$(codex plugin list --json)
  while IFS= read -r plugin; do
    [[ -n $plugin ]] || continue
    if PLUGIN_ID="$plugin" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
target = os.environ["PLUGIN_ID"]
raise SystemExit(0 if any(item.get("pluginId") == target and item.get("enabled") for item in data.get("installed", [])) else 1)
' <<<"$codex_plugins"; then
      pass "Codex plugin $plugin"
    else
      fail "Codex plugin $plugin is not installed and enabled"
    fi
  done <"$ROOT/config/codex-plugins.txt"

  echo "INFO Codex-managed plugin installation is verified in the Plugins tab, not by the CLI:"
  while IFS= read -r plugin; do
    [[ -n $plugin && $plugin != \#* ]] || continue
    echo "INFO   $plugin"
  done <"$ROOT/config/codex-managed-plugins.txt"

  if PLUGIN_ID="$superpowers_plugin_id" PLUGIN_VERSION="$superpowers_version" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
matches = [item for item in data.get("installed", []) if item.get("pluginId", "").startswith("superpowers@")]
expected = os.environ["PLUGIN_ID"]
version = os.environ["PLUGIN_VERSION"]
raise SystemExit(0 if len(matches) == 1 and matches[0].get("pluginId") == expected and matches[0].get("version") == version and matches[0].get("enabled") else 1)
' <<<"$codex_plugins"; then
    pass "Configured Superpowers $superpowers_version is the only Codex Superpowers plugin"
  else
    fail "Codex must enable only $superpowers_plugin_id at $superpowers_version"
  fi

fi

if [[ $runtime == claude ]]; then
  claude_plugins=$(claude plugin list --json)
  while IFS= read -r plugin; do
    [[ -n $plugin ]] || continue
    if PLUGIN_ID="$plugin" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
target = os.environ["PLUGIN_ID"]
raise SystemExit(0 if any(item.get("id") == target and item.get("scope") == "user" and item.get("enabled") for item in data) else 1)
' <<<"$claude_plugins"; then
      pass "Claude plugin $plugin"
    else
      fail "Claude plugin $plugin is not installed and enabled at user scope"
    fi
  done <"$ROOT/config/claude-plugins.txt"

  if PLUGIN_ID="$superpowers_plugin_id" PLUGIN_VERSION="$superpowers_version" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
matches = [item for item in data if item.get("id", "").startswith("superpowers@") and item.get("scope") == "user" and item.get("enabled")]
expected = os.environ["PLUGIN_ID"]
version = os.environ["PLUGIN_VERSION"]
raise SystemExit(0 if len(matches) == 1 and matches[0].get("id") == expected and matches[0].get("version") == version else 1)
' <<<"$claude_plugins"; then
    pass "Configured Superpowers $superpowers_version is the only enabled Claude Superpowers plugin"
  else
    fail "Claude must enable only $superpowers_plugin_id at $superpowers_version"
  fi

  if PLUGIN_ID="$superpowers_plugin_id" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
enabled = data.get("enabledPlugins", {})
raise SystemExit(0 if enabled.get("superpowers@claude-plugins-official") is not True and enabled.get(os.environ["PLUGIN_ID"]) is True else 1)
' <"$claude_config_dir/settings.json"; then
    pass "Claude routes Superpowers to the configured fork"
  else
    fail "Claude must disable official Superpowers and enable $superpowers_plugin_id"
  fi

fi

if [[ $runtime == codex ]]; then
  if python3 - "$codex_home" "$ROOT" <<'PY'; then
import sys
import tomllib
from pathlib import Path

codex_home = Path(sys.argv[1])
repository = Path(sys.argv[2])
config = tomllib.loads((codex_home / "config.toml").read_text())
disabled = {
    Path(item["path"]).resolve()
    for item in config.get("skills", {}).get("config", [])
    if item.get("enabled") is False
}
root = codex_home / "plugins/cache/openai-curated-remote/product-design"
expected = set()
if root.exists():
    for name in ("ideate", "index"):
        expected.update(path.resolve() for path in root.glob(f"*/skills/{name}/SKILL.md"))
expected.add(
    (repository / ".agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md").resolve()
)
raise SystemExit(0 if expected <= disabled else 1)
PY
    pass "Product Design image ideation and duplicate nested skills are disabled"
  else
    fail "Codex skill override policy is incomplete; rerun bootstrap"
  fi

fi

if python3 "$ROOT/scripts/check_skill_ownership.py"; then
  pass "User skill sources and private recovery bindings"
else
  fail "User skill ownership audit failed; run npm run skills:doctor"
fi

if ((failures)); then
  echo "$failures setup check(s) failed." >&2
  exit 1
fi

echo "$runtime setup verified."
