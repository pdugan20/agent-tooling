#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

missing=0
for command_name in npm python3 pre-commit actionlint gitleaks; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    missing=1
  fi
done

for executable in claudelint markdownlint prettier; do
  if [[ ! -x "node_modules/.bin/$executable" ]]; then
    echo "Missing node_modules/.bin/$executable; run npm ci." >&2
    missing=1
  fi
done

if ((missing)); then
  echo "Install repository prerequisites before running verification." >&2
  exit 1
fi

npm test

repository_files=()
while IFS= read -r -d '' file; do
  repository_files+=("$file")
done < <(git ls-files --cached --others --exclude-standard -z)

pre-commit run --files "${repository_files[@]}" --show-diff-on-failure
gitleaks git --redact --no-banner --verbose .
git diff --check

echo "Agent tooling repository verified."
