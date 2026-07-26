#!/usr/bin/env bash

set -euo pipefail

migration_branch=codex/agent-workflow-migration
github_root=${AGENT_GITHUB_ROOT:-"$HOME/Documents/Github"}
messenger_root=${AGENT_MESSENGER_ROOT:-"$HOME/Documents/messenger"}
fetch=false

if [[ ${1:-} == "--fetch" ]]; then
  fetch=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--fetch]" >&2
  exit 2
fi

failed=false

printf '%-28s %-8s %-10s %5s %6s %7s %7s\n' \
  REPOSITORY DEFAULT HEAD AHEAD BEHIND PARENT REMOTE

while IFS='|' read -r repository path; do
  if [[ ! -d $path ]]; then
    printf '%-28s %s\n' "$repository" "missing checkout: $path" >&2
    failed=true
    continue
  fi

  if [[ $fetch == true ]]; then
    git -C "$path" fetch --prune origin >/dev/null
  fi

  default_ref=$(git -C "$path" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -z $default_ref ]]; then
    if git -C "$path" show-ref --verify --quiet refs/remotes/origin/main; then
      default_ref=origin/main
    else
      default_ref=origin/master
    fi
  fi

  if ! git -C "$path" show-ref --verify --quiet "refs/heads/$migration_branch"; then
    printf '%-28s %s\n' "$repository" "missing local branch: $migration_branch" >&2
    failed=true
    continue
  fi

  head=$(git -C "$path" rev-parse --short "$migration_branch")
  ahead=$(git -C "$path" rev-list --count "$default_ref..$migration_branch")
  behind=$(git -C "$path" rev-list --count "$migration_branch..$default_ref")
  merge_base=$(git -C "$path" merge-base "$migration_branch" "$default_ref")
  parent=$(git -C "$path" rev-parse "$migration_branch^")
  parent_state=ok
  [[ $parent == "$merge_base" ]] || parent_state=stale

  remote_state=absent
  remote_output=$(git -C "$path" ls-remote --heads origin "refs/heads/$migration_branch")
  [[ -z $remote_output ]] || remote_state=exists

  printf '%-28s %-8s %-10s %5s %6s %7s %7s\n' \
    "$repository" "${default_ref#origin/}" "$head" "$ahead" "$behind" "$parent_state" "$remote_state"

  if [[ $ahead -ne 1 || $behind -ne 0 || $parent_state != ok || $remote_state != absent ]]; then
    failed=true
  fi
done <<EOF
nextup-ios-app|$github_root/nextup-ios-app
nextup-backend|$github_root/nextup-backend
nextup-web|$github_root/nextup-web
pat-portfolio|$github_root/pat-portfolio
messenger|$messenger_root
chat-app-prototype|$github_root/chat-app-prototype
claude-usage|$github_root/claude-usage
claudelint|$github_root/claudelint
claudenotes|$github_root/claudenotes
e-ink-scoreboard|$github_root/e-ink-scoreboard
figma-chat-builder|$github_root/figma-chat-builder
figma-music-injector|$github_root/figma-music-injector
imessage-swift-prototype|$github_root/imessage-swift-prototype
libby-downloader|$github_root/libby-downloader
mintlify-docs|$github_root/mintlify-docs
passant-prototype|$github_root/passant-prototype
rss-feed-generator|$github_root/rss-feed-generator
touchpoint|$github_root/touchpoint
x-archive|$github_root/x-archive
bibliocommons-mcp|$github_root/bibliocommons-mcp
clickwheel|$github_root/clickwheel
presentations|$github_root/presentations
rewind|$github_root/rewind
EOF

if [[ $failed == true ]]; then
  echo "Migration publication preflight failed." >&2
  exit 1
fi

echo "Migration publication preflight passed."
