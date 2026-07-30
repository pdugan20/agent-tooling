#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
claude_config_dir=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed." >&2
  exit 1
fi

ensure_marketplace() {
  local name=$1
  local source=$2
  if claude plugin marketplace list --json | MARKETPLACE_NAME="$name" python3 -c '
import json, sys
import os
data = json.load(sys.stdin)
target = os.environ["MARKETPLACE_NAME"]
raise SystemExit(0 if any(item.get("name") == target for item in data) else 1)
'; then
    return
  fi
  claude plugin marketplace add "$source"
}

ensure_marketplace pdugan20-plugins pdugan20/pdugan20-plugins
ensure_marketplace superpowers-configured pdugan20/superpowers

installed_plugins=$(claude plugin list --json)
while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  state=$(PLUGIN_ID="$plugin" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
target = os.environ["PLUGIN_ID"]
matches = [item for item in data if item.get("id") == target and item.get("scope") == "user"]
if not matches:
    print("missing")
elif any(item.get("enabled") for item in matches):
    print("enabled")
else:
    print("disabled")
' <<<"$installed_plugins")

  case $state in
    enabled) ;;
    disabled) claude plugin enable "$plugin" --scope user ;;
    missing) claude plugin install "$plugin" --scope user ;;
  esac
done <"$ROOT/config/claude-plugins.txt"

python3 "$ROOT/scripts/configure-claude.py" --settings "$claude_config_dir/settings.json"

echo "Claude plugin set is installed. Restart Claude Code to load updates."
