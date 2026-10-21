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

claude_config_dir=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}
codex_home=${CODEX_HOME:-"$HOME/.codex"}

link_path() {
  local source=$1
  local target=$2

  mkdir -p "$(dirname "$target")"
  if [[ -L $target && $(readlink "$target") == "$source" ]]; then
    return
  fi
  if [[ -e $target || -L $target ]]; then
    echo "Refusing to replace existing path: $target" >&2
    echo "Compare and preserve it before changing its owner; no path was removed." >&2
    exit 1
  fi
  ln -s "$source" "$target"
}

if [[ $runtime == claude ]]; then
  link_path "$ROOT/global/AGENTS.md" "$claude_config_dir/CLAUDE.md"
  for style in "$ROOT"/global/output-styles/*.md; do
    [[ -f $style ]] || continue
    link_path "$style" "$claude_config_dir/output-styles/${style##*/}"
  done
  skills_target="$claude_config_dir/skills"
else
  link_path "$ROOT/global/AGENTS.md" "$codex_home/AGENTS.md"
  skills_target="$HOME/.agents/skills"
fi

for skill_dir in "$ROOT"/.agents/skills/*; do
  [[ -f $skill_dir/SKILL.md ]] || continue
  link_path "$skill_dir" "$skills_target/${skill_dir##*/}"
done

if [[ $runtime == claude ]]; then
  python3 "$ROOT/scripts/configure-claude.py" --settings "$claude_config_dir/settings.json"
else
  python3 "$ROOT/scripts/configure-codex.py" \
    --config "$codex_home/config.toml" \
    --codex-home "$codex_home" \
    --mcp-servers "$ROOT/config/codex-mcp-servers.json" \
    --disable-skill "$ROOT/.agents/skills/swiftui-pro/skills/swiftui-pro/SKILL.md"
fi

echo "$runtime links and routing settings are configured."
