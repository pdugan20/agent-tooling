#!/usr/bin/env bash

set -euo pipefail

if [[ $(uname -s) != Linux || $(uname -m) != x86_64 ]]; then
  echo "install-ci-tools.sh supports only GitHub's Linux x86_64 runner." >&2
  exit 1
fi

: "${RUNNER_TEMP:?RUNNER_TEMP must point at the GitHub Actions temporary directory}"
: "${GITHUB_PATH:?GITHUB_PATH must be available in GitHub Actions}"

tool_dir="$RUNNER_TEMP/agent-tooling-bin"
mkdir -p "$tool_dir"

install_archive() {
  local name=$1
  local version=$2
  local url=$3
  local checksum=$4
  local archive="$RUNNER_TEMP/${name}-${version}.tar.gz"

  curl --fail --silent --show-error --location "$url" --output "$archive"
  echo "$checksum  $archive" | sha256sum --check
  tar -xzf "$archive" -C "$tool_dir" "$name"
  chmod +x "$tool_dir/$name"
}

install_archive \
  actionlint \
  1.7.12 \
  https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz \
  8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8

install_archive \
  gitleaks \
  8.30.0 \
  https://github.com/gitleaks/gitleaks/releases/download/v8.30.0/gitleaks_8.30.0_linux_x64.tar.gz \
  79a3ab579b53f71efd634f3aaf7e04a0fa0cf206b7ed434638d1547a2470a66e

echo "$tool_dir" >>"$GITHUB_PATH"
