#!/usr/bin/env bash

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
claude_config_dir=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}

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
link_path "$ROOT/global/AGENTS.md" "$claude_config_dir/CLAUDE.md"

for legacy_skill in execute-plan feature-delivery formal-spec production-hardening strict-tdd write-plan; do
  remove_legacy_link \
    "$claude_config_dir/skills/$legacy_skill" \
    "$ROOT/plugins/patrick-delivery/skills/$legacy_skill"
done
remove_legacy_link "$HOME/plugins/patrick-delivery" "$ROOT/plugins/patrick-delivery"
remove_legacy_link "$HOME/.agents/plugins/marketplace.json" "$ROOT/.agents/plugins/marketplace.json"

for managed_skill in \
  animation-vocabulary \
  apple-design \
  code-native-ui-ideation \
  emil-design-eng \
  feature-delivery \
  find-animation-opportunities \
  generate-mintlify-reference \
  pick-ui-library \
  production-hardening \
  review-mintlify-docs \
  review-animations \
  scaffold-mintlify-site \
  write-mintlify-changelog \
  swiftui-pro; do
  remove_legacy_link "$HOME/.agents/skills/$managed_skill" "$ROOT/skills/$managed_skill"
  remove_legacy_link "$claude_config_dir/skills/$managed_skill" "$ROOT/skills/$managed_skill"
done

link_skill_collection() {
  local collection=$1
  local skill_dir
  local skill_name

  for skill_dir in "$collection"/*; do
    [[ -f $skill_dir/SKILL.md ]] || continue
    skill_name=${skill_dir##*/}
    link_path "$skill_dir" "$HOME/.agents/skills/$skill_name"
    link_path "$skill_dir" "$claude_config_dir/skills/$skill_name"
  done
}

link_skill_collection "$ROOT/.agents/skills"

python3 "$ROOT/scripts/configure-claude.py" --settings "$claude_config_dir/settings.json"

codex_config="$HOME/.codex/config.toml"
mkdir -p "$(dirname "$codex_config")"
touch "$codex_config"
python3 "$ROOT/scripts/configure-codex.py" \
  --config "$codex_config" \
  --disable-skill "$ROOT/.agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"

echo "Agent tooling links and routing settings are configured."
