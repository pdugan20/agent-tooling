#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

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

claude plugin marketplace update

installed_plugins=$(claude plugin list --json)
while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  if PLUGIN_ID="$plugin" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
target = os.environ["PLUGIN_ID"]
raise SystemExit(0 if any(item.get("id") == target and item.get("scope") == "user" for item in data) else 1)
' <<<"$installed_plugins"; then
    if update_output=$(claude plugin update "$plugin" --scope user 2>&1); then
      printf '%s\n' "$update_output"
    else
      printf '%s\n' "$update_output" >&2
      if [[ $update_output != *"is already enabled at user scope"* ]]; then
        exit 1
      fi
    fi
  else
    claude plugin install "$plugin" --scope user
  fi

  current_plugins=$(claude plugin list --json)
  if PLUGIN_ID="$plugin" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
target = os.environ["PLUGIN_ID"]
raise SystemExit(0 if any(item.get("id") == target and item.get("scope") == "user" and item.get("enabled") for item in data) else 1)
' <<<"$current_plugins"; then
    continue
  fi
  claude plugin enable "$plugin" --scope user
done <"$ROOT/config/claude-plugins.txt"

python3 "$ROOT/scripts/configure-claude.py" --settings "$HOME/.claude/settings.json"

echo "Configured Claude plugins refreshed. Restart Claude Code to load them."
