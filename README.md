# Agent tooling

Private, canonical source for Patrick's cross-repository agent instructions, personal skills, and delivery plugin.

## Start here

- `inventory/manifest.md`: what is owned, installed, runtime-managed, or machine-local.
- `inventory/maintenance.md`: how to update personal workflows, third-party plugins, Superpowers-derived behavior, and Product Design policy.
- `config/codex-plugins.txt` and `config/claude-plugins.txt`: machine-readable desired plugin sets.
- `scripts/verify-setup.sh`: checks that a machine matches the desired setup.
- `scripts/verify-repo.sh`: runs the same repository gate used by GitHub Actions.

## What lives here

- `global/AGENTS.md`: shared working agreement for Codex and Claude Code.
- `skills/`: portable personal skills used by both runtimes.
- `plugins/patrick-delivery/`: proportional feature delivery plus explicit specification, planning, TDD, execution, and hardening workflows.
- `.agents/plugins/marketplace.json`: local Codex marketplace manifest.
- `scripts/bootstrap.sh`: creates runtime symlinks and applies non-secret routing settings.
- `scripts/install-codex-plugins.sh`: installs the portable plugin set on a new machine.
- `scripts/install-claude-plugins.sh`: installs and enables the desired Claude compatibility set.
- `scripts/refresh-codex-plugins.sh`: refreshes configured marketplace plugins and reapplies local skill policy.
- `scripts/refresh-claude-plugins.sh`: refreshes and re-enables the desired Claude compatibility set.
- `scripts/setup-new-machine.sh`: applies the complete agent layer on a prepared Mac.
- `scripts/verify-setup.sh`: verifies links, plugins, Superpowers state, and Product Design policy.
- `scripts/audit-migration-branches.sh`: checks migration branches before publication or verifies recorded merges afterward.

## Setup on another machine

First install and authenticate Codex, Claude Code, and GitHub CLI. Then clone this repository and run:

```bash
mkdir -p ~/Documents/Github
gh repo clone pdugan20/agent-tooling ~/Documents/Github/agent-tooling
cd ~/Documents/Github/agent-tooling
./scripts/setup-new-machine.sh
```

Restart Codex and Claude afterward. Authenticate Figma, GitHub, Firebase, Sentry, and other connectors in their normal secure flows. Install Xcode/simulators, Node, Firebase CLI, and project dependencies separately; the setup script intentionally manages only the agent layer.

The bootstrap script refuses to replace existing non-symlink files. Review or move conflicting files first. It also applies non-secret, machine-local Codex policy and repairs when relevant: keeping the Claude fallback filename at TOML top level, resolving the installed Computer Use executable to its absolute path, and disabling Product Design's generated-image router and ideation skill.

## Runtime mapping

- Codex reads the global agreement through `~/.codex/AGENTS.md`.
- Claude reads the same file through `~/.claude/CLAUDE.md`.
- Portable skills are linked into both `~/.agents/skills` and `~/.claude/skills`.
- The delivery skills stay canonical inside the plugin. Codex uses their plugin namespace; Claude receives direct personal-skill symlinks to the same folders.

The substantial `feature-delivery` workflow may trigger automatically for production feature implementation. Invoke strict component workflows explicitly:

- Codex: `$patrick-delivery:strict-tdd`, `$patrick-delivery:write-plan`, or another `patrick-delivery` skill.
- Claude: `/strict-tdd`, `/write-plan`, or another linked delivery skill.

Claude's official Superpowers plugin is disabled by the bootstrap because Claude cannot apply `skillOverrides` to plugin-provided skills. The shared delivery skills provide the intentional opt-in replacement without maintaining two copies.

Do not temporarily enable the full Superpowers bundle. Review useful upstream changes and port them intentionally into the canonical personal implementation so its mandatory brainstorming, browser chooser, worktree, and TDD policies cannot leak into lightweight work.

See `inventory/maintenance.md` for personal-skill, Superpowers-review, Product Design, and third-party plugin update procedures.

## Repository development

Install the small repository-only toolchain, then use the same verification command locally and in CI:

```bash
nvm install
nvm use
npm ci
python3 -m pip install pre-commit==4.6.1
brew install actionlint gitleaks
pre-commit install --hook-type pre-commit --hook-type pre-push
npm run verify
```

`npm run verify` runs unit tests, pinned pre-commit linters, ClaudeLint, Markdownlint, Ruff, ShellCheck, shfmt, actionlint, repository policy assertions, a full-history Gitleaks scan, and whitespace checks. The pre-commit hook scans staged changes, while the pre-push hook scans the full Git history. Verification intentionally does not run `scripts/verify-setup.sh`, because setup verification depends on authenticated machine-local Codex and Claude state.

CI uses one stable required job named `ci`. Dependabot proposes grouped npm and GitHub Actions updates after a 14-day cooldown.

GitHub-native secret scanning and push protection are unavailable for this user-owned private repository under the current account model. The required `ci` check plus staged-change, pre-push, and full-history Gitleaks scans are the deliberate no-billing fallback. Do not enable GitHub Secret Protection or change repository ownership/visibility merely to replace this fallback without a separate product and billing decision.

## Patrick Delivery releases

The version in `plugins/patrick-delivery/.codex-plugin/plugin.json` is the source of truth. Bump it only when Patrick Delivery behavior changes, merge the verified change, and then create and push an annotated tag named `patrick-delivery-vMAJOR.MINOR.PATCH`.

The tag workflow verifies that the tag matches the manifest, runs the complete repository gate, and creates a GitHub Release with generated notes. It does not publish to npm or another public registry. See `inventory/maintenance.md` for the exact release checklist.

## What does not sync automatically

Git carries the files, but each machine still needs the bootstrap. OAuth sessions, API keys, trusted-workspace decisions, plugin authentication, app settings, and repository-local `AGENTS.md` files remain machine- or repository-local. Never commit those credentials here.

## Updating

Edit canonical files in this repository, validate them, commit, and push to the private remote. Other machines receive changes after `git pull`; run `./scripts/bootstrap.sh`, `./scripts/refresh-codex-plugins.sh`, and `./scripts/refresh-claude-plugins.sh`, then start new Claude and Codex tasks so manifests, skill inventories, and machine-local policy are refreshed.
