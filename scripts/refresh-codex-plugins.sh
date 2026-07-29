#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed." >&2
  exit 1
fi

ensure_marketplace() {
  local name=$1
  local source=$2
  if ! codex plugin marketplace list | awk -v target="$name" '$1 == target { found = 1 } END { exit !found }'; then
    codex plugin marketplace add "$source"
  fi
}

ensure_marketplace pdugan20-plugins https://github.com/pdugan20/pdugan20-plugins.git
ensure_marketplace superpowers-configured https://github.com/pdugan20/superpowers.git
ensure_marketplace mintlify-marketplace https://github.com/mintlify/mintlify-claude-plugin.git

codex plugin marketplace upgrade

while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  echo "Refreshing $plugin"
  codex plugin add "$plugin"
done <"$ROOT/config/codex-plugins.txt"

python3 "$ROOT/scripts/configure-codex.py" --config "$HOME/.codex/config.toml"

echo "Marketplace-installed Codex plugins refreshed."
echo "Codex-managed plugins update separately through the Plugins tab. Start a new task to load changes."
