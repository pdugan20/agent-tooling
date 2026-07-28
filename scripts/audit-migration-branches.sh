#!/usr/bin/env bash

set -euo pipefail

migration_branch=codex/agent-workflow-migration
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
default_repositories_root=$(cd "$root/.." && pwd)
repositories_root=${AGENT_REPOSITORIES_ROOT:-${AGENT_GITHUB_ROOT:-$default_repositories_root}}
if [[ -n ${AGENT_MESSENGER_ROOT:-} ]]; then
  messenger_root=$AGENT_MESSENGER_ROOT
elif [[ -d $repositories_root/messenger ]]; then
  messenger_root=$repositories_root/messenger
else
  messenger_root=$(cd "$repositories_root/.." && pwd)/messenger
fi
fetch=false
published=false
merged=false

for argument in "$@"; do
  case $argument in
    --fetch) fetch=true ;;
    --published) published=true ;;
    --merged) merged=true ;;
    *)
      echo "Usage: $0 [--fetch] [--published|--merged]" >&2
      exit 2
      ;;
  esac
done

if [[ $published == true && $merged == true ]]; then
  echo "Choose only one of --published or --merged." >&2
  exit 2
fi

failed=false

if [[ $merged == true ]]; then
  printf '%-28s %-8s %-10s %-9s %7s\n' \
    REPOSITORY DEFAULT MERGE STATE REMOTE
else
  printf '%-28s %-8s %-10s %5s %6s %7s %7s\n' \
    REPOSITORY DEFAULT HEAD AHEAD BEHIND PARENT REMOTE
fi

while IFS='|' read -r repository repository_path merge_commit; do
  if [[ ! -d $repository_path ]]; then
    printf '%-28s %s\n' "$repository" "missing checkout: $repository_path" >&2
    failed=true
    continue
  fi

  if [[ $fetch == true ]]; then
    git -C "$repository_path" fetch --prune origin >/dev/null
  fi

  default_ref=$(git -C "$repository_path" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -z $default_ref ]]; then
    if git -C "$repository_path" show-ref --verify --quiet refs/remotes/origin/main; then
      default_ref=origin/main
    else
      default_ref=origin/master
    fi
  fi

  remote_output=$(git -C "$repository_path" ls-remote --heads origin "refs/heads/$migration_branch")
  if [[ -z $remote_output ]]; then
    remote_state=absent
  else
    remote_state=present
  fi

  if [[ $merged == true ]]; then
    merge_state=missing
    if git -C "$repository_path" cat-file -e "$merge_commit^{commit}" 2>/dev/null &&
      git -C "$repository_path" merge-base --is-ancestor "$merge_commit" "$default_ref"; then
      merge_state=included
    fi

    printf '%-28s %-8s %-10s %-9s %7s\n' \
      "$repository" "${default_ref#origin/}" "${merge_commit:0:8}" "$merge_state" "$remote_state"

    if [[ $merge_state != included || $remote_state != absent ]]; then
      failed=true
    fi
    continue
  fi

  if ! git -C "$repository_path" show-ref --verify --quiet "refs/heads/$migration_branch"; then
    printf '%-28s %s\n' "$repository" "missing local branch: $migration_branch" >&2
    failed=true
    continue
  fi

  head=$(git -C "$repository_path" rev-parse --short "$migration_branch")
  ahead=$(git -C "$repository_path" rev-list --count "$default_ref..$migration_branch")
  behind=$(git -C "$repository_path" rev-list --count "$migration_branch..$default_ref")
  merge_base=$(git -C "$repository_path" merge-base "$migration_branch" "$default_ref")
  parent=$(git -C "$repository_path" rev-parse "$migration_branch^")
  parent_state=ok
  [[ $parent == "$merge_base" ]] || parent_state=stale

  local_head=$(git -C "$repository_path" rev-parse "$migration_branch")
  remote_head=${remote_output%%[[:space:]]*}
  if [[ -z $remote_output ]]; then
    remote_state=absent
  elif [[ $remote_head == "$local_head" ]]; then
    remote_state=match
  else
    remote_state=differs
  fi

  printf '%-28s %-8s %-10s %5s %6s %7s %7s\n' \
    "$repository" "${default_ref#origin/}" "$head" "$ahead" "$behind" "$parent_state" "$remote_state"

  expected_remote_state=absent
  [[ $published == true ]] && expected_remote_state=match

  if [[ $ahead -ne 1 || $behind -ne 0 || $parent_state != ok || $remote_state != "$expected_remote_state" ]]; then
    failed=true
  fi
done <<EOF
nextup-ios-app|$repositories_root/nextup-ios-app|2f89c7292c8d11c0354ffa0dfdc2ac81bc86e587
nextup-backend|$repositories_root/nextup-backend|68a6de4a1a29fdda9d1874e51bf4f42e83503f2e
nextup-web|$repositories_root/nextup-web|ae835097a6d84fa175a31f66ea530a48e8072b33
pat-portfolio|$repositories_root/pat-portfolio|7308d50fa7dca7cef0560bb2ca2af90f9648c626
messenger|$messenger_root|9d339b9853fdf46ebd6fea2d89f8bebd22b40767
chat-app-prototype|$repositories_root/chat-app-prototype|b81724f3ab149d60b6aa54a29431025e0e6d4be4
claude-usage|$repositories_root/claude-usage|f73384ad21ca7f9277e50f03dc223a42e5f9deff
claudelint|$repositories_root/claudelint|016b46d21e6cffb8da3ffa931b75f94a88fb3639
claudenotes|$repositories_root/claudenotes|ee21f2760ba789e138fae7d97934e96b0731ab1d
e-ink-scoreboard|$repositories_root/e-ink-scoreboard|2ee6682fca0d4a3a01492c509e9e7077e92ba4c3
figma-chat-builder|$repositories_root/figma-chat-builder|93e77b926f956e9e6713264a51cfcb3dc6e4624a
figma-music-injector|$repositories_root/figma-music-injector|6f842d8167c8df4f830dbfc1e1b9887216cb4952
imessage-swift-prototype|$repositories_root/imessage-swift-prototype|fe5a878ee3f2957b19cfc6742ffab7d5733a20ad
libby-downloader|$repositories_root/libby-downloader|9c9ac8440edd7a4d7cb357fe54397d53b47f1882
mintlify-docs|$repositories_root/mintlify-docs|222fb1d59f6e683419b380343b5c7cea72a327b6
passant-prototype|$repositories_root/passant-prototype|739d7f93829bcb8eb9aabcc65145c961f5d5e3d3
rss-feed-generator|$repositories_root/rss-feed-generator|de98a45a5a7426e19cb65f1ab7d4b280a381ef92
touchpoint|$repositories_root/touchpoint|8a823933280240eb5b31f6eea085fe18444f816b
x-archive|$repositories_root/x-archive|712e3705cecbf993b4b2c66b2fa027eceef146bf
bibliocommons-mcp|$repositories_root/bibliocommons-mcp|d04267b75d8d2745359153f25a48260f5812061d
clickwheel|$repositories_root/clickwheel|9cf8833e80f455440fdde009da909cb162666aa1
presentations|$repositories_root/presentations|d39b9f6c7b9b4cb0bdaa90af0c9b52d2f9353de8
rewind|$repositories_root/rewind|c0bb6a0a66b1bf1400e0b320a8449a622f966654
EOF

if [[ $failed == true ]]; then
  echo "Migration branch audit failed." >&2
  exit 1
fi

if [[ $merged == true ]]; then
  echo "Merged migration audit passed."
elif [[ $published == true ]]; then
  echo "Published migration branch audit passed."
else
  echo "Migration publication preflight passed."
fi
