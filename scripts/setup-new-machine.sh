#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
runtime=codex
if (($#)); then
  if [[ $# == 1 && $1 == --claude ]]; then
    runtime=claude
  else
    echo "Usage: $0 [--claude]" >&2
    exit 2
  fi
fi

if ! command -v "$runtime" >/dev/null 2>&1; then
  echo "$runtime CLI is not installed." >&2
  exit 1
fi

if [[ $runtime == claude ]]; then
  if ! command -v typescript-language-server >/dev/null 2>&1; then
    if ! command -v npm >/dev/null 2>&1; then
      echo "Node.js and npm are required to install the Claude TypeScript language server." >&2
      exit 1
    fi
    npm install --global typescript typescript-language-server
  fi
  "$ROOT/scripts/bootstrap.sh" --claude
  "$ROOT/scripts/install-claude-plugins.sh"
  "$ROOT/scripts/verify-setup.sh" --claude
else
  "$ROOT/scripts/bootstrap.sh"
  "$ROOT/scripts/install-codex-plugins.sh"
  "$ROOT/scripts/verify-setup.sh"
fi

echo "$runtime setup is complete. Restart its harness, then authenticate connectors as needed."
