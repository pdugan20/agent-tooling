# Agent tooling

Private, canonical source for Patrick's cross-repository agent instructions, personal skills, and delivery plugin.

## What lives here

- `global/AGENTS.md`: shared working agreement for Codex and Claude Code.
- `skills/`: portable personal skills used by both runtimes.
- `plugins/patrick-delivery/`: explicit specification, planning, TDD, execution, and hardening workflows for Codex.
- `.agents/plugins/marketplace.json`: local Codex marketplace manifest.
- `scripts/bootstrap.sh`: creates runtime symlinks and applies non-secret routing settings.
- `scripts/install-codex-plugins.sh`: installs the portable plugin set on a new machine.
- `scripts/audit-migration-branches.sh`: checks migration branches before publication or verifies recorded merges afterward.

## Setup on another machine

Clone this repository, then run:

```bash
./scripts/bootstrap.sh
./scripts/install-codex-plugins.sh
```

The bootstrap script refuses to replace existing non-symlink files. Review or move conflicting files first. It also applies two non-secret, machine-local Codex repairs when relevant: keeping the Claude fallback filename at TOML top level and resolving the installed Computer Use executable to its absolute path.

## Runtime mapping

- Codex reads the global agreement through `~/.codex/AGENTS.md`.
- Claude reads the same file through `~/.claude/CLAUDE.md`.
- Portable skills are linked into both `~/.agents/skills` and `~/.claude/skills`.
- The delivery skills stay canonical inside the plugin. Codex uses their plugin namespace; Claude receives direct personal-skill symlinks to the same folders.

Invoke strict workflows explicitly:

- Codex: `$patrick-delivery:strict-tdd`, `$patrick-delivery:write-plan`, or another `patrick-delivery` skill.
- Claude: `/strict-tdd`, `/write-plan`, or another linked delivery skill.

Claude's official Superpowers plugin is disabled by the bootstrap because Claude cannot apply `skillOverrides` to plugin-provided skills. The shared delivery skills provide the intentional opt-in replacement without maintaining two copies.

If a workflow exists only in Superpowers, enable the plugin for that session of work and disable it afterward:

```bash
claude plugin enable superpowers@claude-plugins-official --scope user
claude plugin disable superpowers@claude-plugins-official --scope user
```

## What does not sync automatically

Git carries the files, but each machine still needs the bootstrap. OAuth sessions, API keys, trusted-workspace decisions, plugin authentication, app settings, and repository-local `AGENTS.md` files remain machine- or repository-local. Never commit those credentials here.

## Updating

Edit canonical files in this repository, validate them, commit, and push to the private remote. Other machines receive changes after `git pull`; symlinked runtimes see the updated files immediately.
