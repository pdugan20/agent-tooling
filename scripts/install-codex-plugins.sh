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
ensure_marketplace mintlify-marketplace https://github.com/mintlify/mintlify-claude-plugin.git
ensure_marketplace patrick-tools https://github.com/pdugan20/patrick-tools.git
ensure_marketplace superpowers-configured https://github.com/pdugan20/superpowers.git

installed_plugins=$(codex plugin list --json)
codex_cache_root=${CODEX_HOME:-"$HOME/.codex"}/plugins/cache
while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  if PLUGIN_ID="$plugin" python3 -c 'import json, os, sys; data=json.load(sys.stdin); target=os.environ["PLUGIN_ID"]; raise SystemExit(0 if any(item.get("pluginId") == target for item in data.get("installed", [])) else 1)' <<<"$installed_plugins"; then
    continue
  fi
  codex plugin add "$plugin"
done <"$ROOT/config/codex-plugins.txt"

for retired_plugin in \
  patrick-delivery@personal \
  mintlify-docs@pdugan20-plugins \
  superpowers@claude-plugins-official \
  superpowers@openai-curated \
  expo@openai-curated \
  sentry@openai-curated \
  mintlify@claude-plugins-official \
  figma@openai-curated \
  github@openai-curated \
  vercel@openai-curated; do
  plugin_name=${retired_plugin%@*}
  marketplace_name=${retired_plugin#*@}
  retired_cache_root=$codex_cache_root/$marketplace_name/$plugin_name
  if PLUGIN_ID="$retired_plugin" python3 -c 'import json, os, sys; data=json.load(sys.stdin); target=os.environ["PLUGIN_ID"]; raise SystemExit(0 if any(item.get("pluginId") == target for item in data.get("installed", [])) else 1)' <<<"$installed_plugins"; then
    codex plugin remove "$retired_plugin"
  elif [[ $marketplace_name != openai-curated && $marketplace_name != claude-plugins-official && -e $retired_cache_root ]]; then
    # Codex can remove an orphaned cache even after its marketplace is gone.
    codex plugin remove "$retired_plugin"
  fi
done

if codex plugin marketplace list | awk -v target="pdugan20-plugins" '$1 == target { found = 1 } END { exit !found }'; then
  codex plugin marketplace remove pdugan20-plugins
fi

echo "Marketplace-installed Codex plugin set is installed."
echo "Verify config/codex-managed-plugins.txt in the Codex Plugins tab and complete any connector authentication there."
