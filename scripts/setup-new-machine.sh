#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if ! command -v typescript-language-server >/dev/null 2>&1; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "Node.js and npm are required to install the Claude TypeScript language server." >&2
    exit 1
  fi
  npm install --global typescript typescript-language-server
fi

"$ROOT/scripts/bootstrap.sh"
"$ROOT/scripts/install-codex-plugins.sh"
"$ROOT/scripts/install-claude-plugins.sh"
"$ROOT/scripts/verify-setup.sh"

echo "Agent tooling setup is complete. Restart Codex and Claude, then authenticate connectors as needed."
