#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed." >&2
  exit 1
fi

if ! codex plugin marketplace list | awk '$1 == "superpowers-configured" { found = 1 } END { exit !found }'; then
  codex plugin marketplace add https://github.com/pdugan20/superpowers.git
fi

codex plugin marketplace upgrade

while IFS= read -r plugin; do
  [[ -n $plugin ]] || continue
  echo "Refreshing $plugin"
  codex plugin add "$plugin"
done <"$ROOT/config/codex-plugins.txt"

python3 "$ROOT/scripts/configure-codex.py" --config "$HOME/.codex/config.toml"

echo "Configured Codex plugins refreshed. Start a new Codex task to load them."
