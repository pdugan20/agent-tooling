#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed." >&2
  exit 1
fi

installed_plugins=$(codex plugin list --json)
for retired_plugin in \
  mintlify-docs@patrick-plugins \
  mintlify-docs@pdugan20-plugins \
  mintlify-docs@patrick-tools \
  patrick-workflows@pdugan20-plugins \
  patrick-workflows@patrick-tools; do
  if PLUGIN_ID="$retired_plugin" python3 -c 'import json, os, sys; data=json.load(sys.stdin); target=os.environ["PLUGIN_ID"]; raise SystemExit(0 if any(item.get("pluginId") == target for item in data.get("installed", [])) else 1)' <<<"$installed_plugins"; then
    codex plugin remove "$retired_plugin"
  fi
done
for retired_marketplace in pdugan20-plugins patrick-tools; do
  if codex plugin marketplace list | awk -v target="$retired_marketplace" '$1 == target { found = 1 } END { exit !found }'; then
    codex plugin marketplace remove "$retired_marketplace"
  fi
done

ensure_marketplace() {
  local name=$1
  local source=$2
  if ! codex plugin marketplace list | awk -v target="$name" '$1 == target { found = 1 } END { exit !found }'; then
    codex plugin marketplace add "$source"
  fi
}

ensure_marketplace patrick-plugins https://github.com/pdugan20/plugins.git
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
