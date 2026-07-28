#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
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

check_link() {
  local source=$1
  local target=$2
  if [[ -L $target && $(readlink "$target") == "$source" ]]; then
    pass "$target"
  else
    fail "$target should link to $source"
  fi
}

check_link "$ROOT/global/AGENTS.md" "$HOME/.codex/AGENTS.md"
check_link "$ROOT/global/AGENTS.md" "$HOME/.claude/CLAUDE.md"

check_skill_collection() {
  local collection=$1
  local skill_dir
  local skill_name

  for skill_dir in "$collection"/*; do
    [[ -f $skill_dir/SKILL.md ]] || continue
    skill_name=${skill_dir##*/}
    check_link "$skill_dir" "$HOME/.agents/skills/$skill_name"
    check_link "$skill_dir" "$HOME/.claude/skills/$skill_name"
  done
}

check_skill_collection "$ROOT/skills"
check_skill_collection "$ROOT/.agents/skills"

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
matches = [item for item in data if item.get("id") == os.environ["PLUGIN_ID"] and item.get("scope") == "user"]
raise SystemExit(0 if len(matches) == 1 and matches[0].get("enabled") and matches[0].get("version") == os.environ["PLUGIN_VERSION"] else 1)
' <<<"$claude_plugins"; then
  pass "Configured Superpowers $superpowers_version is enabled in Claude"
else
  fail "Claude must enable $superpowers_plugin_id at $superpowers_version"
fi

if PLUGIN_ID="$superpowers_plugin_id" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
enabled = data.get("enabledPlugins", {})
raise SystemExit(0 if enabled.get("superpowers@claude-plugins-official") is False and enabled.get(os.environ["PLUGIN_ID"]) is True else 1)
' <"$HOME/.claude/settings.json"; then
  pass "Claude routes Superpowers to the configured fork"
else
  fail "Claude must disable official Superpowers and enable $superpowers_plugin_id"
fi

if python3 - "$HOME" "$ROOT" <<'PY'; then
import sys
import tomllib
from pathlib import Path

home = Path(sys.argv[1])
repository = Path(sys.argv[2])
config = tomllib.loads((home / ".codex/config.toml").read_text())
disabled = {
    Path(item["path"]).resolve()
    for item in config.get("skills", {}).get("config", [])
    if item.get("enabled") is False
}
root = home / ".codex/plugins/cache/openai-curated-remote/product-design"
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

if ((failures)); then
  echo "$failures setup check(s) failed." >&2
  exit 1
fi

echo "Agent tooling setup verified."
