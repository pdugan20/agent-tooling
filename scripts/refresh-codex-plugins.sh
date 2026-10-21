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

ensure_marketplace firebase https://github.com/firebase/skills.git
ensure_marketplace cloudflare https://github.com/cloudflare/skills.git
ensure_marketplace claude-plugins-official https://github.com/anthropics/claude-plugins-official.git
ensure_marketplace patrick-plugins https://github.com/pdugan20/plugins.git
ensure_marketplace superpowers-configured https://github.com/pdugan20/superpowers.git
ensure_marketplace mintlify-marketplace https://github.com/mintlify/mintlify-claude-plugin.git

marketplaces=$(python3 -c 'import sys; print("\n".join(sorted({line.strip().rsplit("@", 1)[1] for line in open(sys.argv[1]) if line.strip() and not line.lstrip().startswith("#")})))' "$ROOT/config/codex-plugins.txt")
while IFS= read -r marketplace; do
  codex plugin marketplace upgrade "$marketplace"
done <<<"$marketplaces"

while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  echo "Refreshing $plugin"
  codex plugin add "$plugin"
done <"$ROOT/config/codex-plugins.txt"

python3 "$ROOT/scripts/configure-codex.py" --config "${CODEX_HOME:-$HOME/.codex}/config.toml" \
  --codex-home "${CODEX_HOME:-$HOME/.codex}"

echo "Marketplace-installed Codex plugins refreshed."
echo "Codex-managed plugins update separately through the Plugins tab. Start a new task to load changes."
