#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

link_path() {
  local source=$1
  local target=$2

  mkdir -p "$(dirname "$target")"
  if [[ -L $target && $(readlink "$target") == "$source" ]]; then
    return
  fi
  if [[ -e $target || -L $target ]]; then
    echo "Refusing to replace existing path: $target" >&2
    echo "Move it aside, then rerun bootstrap." >&2
    exit 1
  fi
  ln -s "$source" "$target"
}

remove_legacy_link() {
  local target=$1
  local expected_prefix=$2

  if [[ -L $target && $(readlink "$target") == "$expected_prefix"* ]]; then
    unlink "$target"
  fi
}

link_path "$ROOT/global/AGENTS.md" "$HOME/.codex/AGENTS.md"
link_path "$ROOT/global/AGENTS.md" "$HOME/.claude/CLAUDE.md"

for legacy_skill in execute-plan feature-delivery formal-spec production-hardening strict-tdd write-plan; do
  remove_legacy_link \
    "$HOME/.claude/skills/$legacy_skill" \
    "$ROOT/plugins/patrick-delivery/skills/$legacy_skill"
done
remove_legacy_link "$HOME/plugins/patrick-delivery" "$ROOT/plugins/patrick-delivery"
remove_legacy_link "$HOME/.agents/plugins/marketplace.json" "$ROOT/.agents/plugins/marketplace.json"

for upstream_skill in animation-vocabulary apple-design emil-design-eng review-animations swiftui-pro; do
  remove_legacy_link "$HOME/.agents/skills/$upstream_skill" "$ROOT/skills/$upstream_skill"
  remove_legacy_link "$HOME/.claude/skills/$upstream_skill" "$ROOT/skills/$upstream_skill"
done

link_skill_collection() {
  local collection=$1
  local skill_dir
  local skill_name

  for skill_dir in "$collection"/*; do
    [[ -f $skill_dir/SKILL.md ]] || continue
    skill_name=${skill_dir##*/}
    link_path "$skill_dir" "$HOME/.agents/skills/$skill_name"
    link_path "$skill_dir" "$HOME/.claude/skills/$skill_name"
  done
}

link_skill_collection "$ROOT/skills"
link_skill_collection "$ROOT/.agents/skills"

python3 "$ROOT/scripts/configure-claude.py" --settings "$HOME/.claude/settings.json"

codex_config="$HOME/.codex/config.toml"
mkdir -p "$(dirname "$codex_config")"
touch "$codex_config"
python3 "$ROOT/scripts/configure-codex.py" \
  --config "$codex_config" \
  --disable-skill "$ROOT/.agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"

echo "Agent tooling links and routing settings are configured."
