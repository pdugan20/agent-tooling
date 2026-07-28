#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

"$ROOT/scripts/bootstrap.sh"
"$ROOT/scripts/install-codex-plugins.sh"
"$ROOT/scripts/install-claude-plugins.sh"
"$ROOT/scripts/verify-setup.sh"

echo "Agent tooling setup is complete. Restart Codex and Claude, then authenticate connectors as needed."
