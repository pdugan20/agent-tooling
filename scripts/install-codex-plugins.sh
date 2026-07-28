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

ensure_marketplace personal "$HOME"
ensure_marketplace firebase https://github.com/firebase/skills.git
ensure_marketplace cloudflare https://github.com/cloudflare/skills.git
ensure_marketplace claude-plugins-official https://github.com/anthropics/claude-plugins-official.git

installed_plugins=$(codex plugin list --json)
while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  if PLUGIN_ID="$plugin" python3 -c 'import json, os, sys; data=json.load(sys.stdin); target=os.environ["PLUGIN_ID"]; raise SystemExit(0 if any(item.get("pluginId") == target for item in data.get("installed", [])) else 1)' <<<"$installed_plugins"; then
    continue
  fi
  codex plugin add "$plugin"
done <"$ROOT/config/codex-plugins.txt"

echo "Codex plugin set is installed. Complete any connector authentication in the app."
