#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed." >&2
  exit 1
fi

if ! codex plugin marketplace list | awk '$1 == "personal" { found = 1 } END { exit !found }'; then
  codex plugin marketplace add "$HOME"
fi

if ! codex plugin marketplace list | awk '$1 == "firebase" { found = 1 } END { exit !found }'; then
  codex plugin marketplace add https://github.com/firebase/skills.git
fi

installed_plugins=$(codex plugin list --json)
while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  if PLUGIN_ID="$plugin" python3 -c 'import json, os, sys; data=json.load(sys.stdin); target=os.environ["PLUGIN_ID"]; raise SystemExit(0 if any(item.get("pluginId") == target for item in data.get("installed", [])) else 1)' <<< "$installed_plugins"; then
    continue
  fi
  codex plugin add "$plugin"
done < "$ROOT/config/codex-plugins.txt"

echo "Codex plugin set is installed. Complete any connector authentication in the app."
