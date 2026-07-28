#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed." >&2
  exit 1
fi

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
    claude plugin update "$plugin" --scope user
  else
    claude plugin install "$plugin" --scope user
  fi
  claude plugin enable "$plugin" --scope user
done <"$ROOT/config/claude-plugins.txt"

python3 "$ROOT/scripts/configure-claude.py" --settings "$HOME/.claude/settings.json"

echo "Configured Claude plugins refreshed. Restart Claude Code to load them."
