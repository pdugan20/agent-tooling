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
  local member=${5:-$name}
  local archive="$RUNNER_TEMP/${name}-${version}.tar.gz"
  local extract_dir="$RUNNER_TEMP/${name}-${version}"

  curl --fail --silent --show-error --location "$url" --output "$archive"
  echo "$checksum  $archive" | sha256sum --check
  mkdir -p "$extract_dir"
  tar -xzf "$archive" -C "$extract_dir" "$member"
  install -m 0755 "$extract_dir/${member#./}" "$tool_dir/$name"
}

install_archive \
  actionlint \
  1.7.12 \
  https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz \
  8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8

install_archive \
  gitleaks \
  8.30.1 \
  https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
  551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb

install_archive \
  typos \
  1.48.0 \
  https://github.com/crate-ci/typos/releases/download/v1.48.0/typos-v1.48.0-x86_64-unknown-linux-musl.tar.gz \
  72a930c9a94fc3914aa56835c5b859c892a797d40c1c42638b98d93f16ff519c \
  ./typos

install_archive \
  zizmor \
  1.28.0 \
  https://github.com/zizmorcore/zizmor/releases/download/v1.28.0/zizmor-x86_64-unknown-linux-gnu.tar.gz \
  e87b67160194884e375a46a12c57ccc904f762b53845f254fab7f17d98809c09

echo "$tool_dir" >>"$GITHUB_PATH"
