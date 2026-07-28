#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
failures=0

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

for skill_dir in "$ROOT"/skills/*; do
  [[ -f $skill_dir/SKILL.md ]] || continue
  skill_name=${skill_dir##*/}
  check_link "$skill_dir" "$HOME/.agents/skills/$skill_name"
  check_link "$skill_dir" "$HOME/.claude/skills/$skill_name"
done

for skill_dir in "$ROOT"/plugins/patrick-delivery/skills/*; do
  [[ -f $skill_dir/SKILL.md ]] || continue
  skill_name=${skill_dir##*/}
  check_link "$skill_dir" "$HOME/.claude/skills/$skill_name"
done

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

if python3 -c '
import json, sys
data = json.load(sys.stdin)
raise SystemExit(0 if not any(item.get("pluginId", "").startswith("superpowers@") for item in data.get("installed", [])) else 1)
' <<<"$codex_plugins"; then
  pass "Superpowers is not installed in Codex"
else
  fail "Superpowers should not be installed in Codex"
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

if python3 -c '
import json, sys
data = json.load(sys.stdin)
enabled = data.get("enabledPlugins", {}).get("superpowers@claude-plugins-official")
raise SystemExit(0 if enabled is False else 1)
' <"$HOME/.claude/settings.json"; then
  pass "Superpowers is disabled in Claude"
else
  fail "Superpowers should be disabled in Claude"
fi

if python3 - "$HOME" <<'PY'; then
import sys
import tomllib
from pathlib import Path

home = Path(sys.argv[1])
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
raise SystemExit(0 if expected <= disabled else 1)
PY
  pass "Product Design image ideation is disabled"
else
  fail "Product Design index/ideate policy is incomplete; rerun bootstrap"
fi

if ((failures)); then
  echo "$failures setup check(s) failed." >&2
  exit 1
fi

echo "Agent tooling setup verified."
