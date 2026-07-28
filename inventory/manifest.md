# Agent tooling manifest

This is the authoritative map of Patrick's shared Claude and Codex setup. The private Git repository at `pdugan20/agent-tooling` is the canonical source; runtime caches and settings under the home directory are generated machine state.

## Canonical sources

| Concern                      | Canonical source                             | Runtime destination                                |
| ---------------------------- | -------------------------------------------- | -------------------------------------------------- |
| Global working agreement     | `global/AGENTS.md`                           | `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`     |
| Locally maintained workflows | `skills/*/SKILL.md`                          | `~/.agents/skills/*` and `~/.claude/skills/*`      |
| Locked upstream skills       | `.agents/skills/*` and `skills-lock.json`    | `~/.agents/skills/*` and `~/.claude/skills/*`      |
| Configured Superpowers state | `config/superpowers.json`                    | Fork repository and both products' plugin caches   |
| Desired Codex plugins        | `config/codex-plugins.txt`                   | `~/.codex/config.toml` and Codex plugin caches     |
| Desired Claude plugins       | `config/claude-plugins.txt`                  | `~/.claude/settings.json` and Claude plugin caches |
| Personal plugin marketplace  | `pdugan20/pdugan20-plugins`                  | Both products' marketplace snapshots               |
| Codex machine policy         | `scripts/configure-codex.py`                 | `~/.codex/config.toml`                              |
| Claude machine policy        | `scripts/configure-claude.py`                | `~/.claude/settings.json`                           |
| Repository-specific guidance | Each repository's `AGENTS.md`                | Travels with that repository                       |

Do not edit generated runtime cache files. Edit this repository, rerun the setup scripts, and start a new task.

## Locally maintained workflows

These are authored or adapted as part of this repository and live under `skills/`:

- `code-native-ui-ideation`
- `feature-delivery`
- `production-hardening`

`feature-delivery` may run automatically for a substantial production implementation. `production-hardening` is
explicit-only. These are skills—not a plugin, a fork, or copies of Superpowers workflows—and use the same canonical
files in Codex and Claude.

## Locked upstream skills

Third-party skills are installed through the official [`skills` CLI](https://github.com/vercel-labs/skills) at
project scope. The CLI owns `.agents/skills/`, creates the `.claude/skills/` compatibility links, and records source
and content hashes in `skills-lock.json`.

| Skill                  | Original source                            | Creator        |
| ---------------------- | ------------------------------------------ | -------------- |
| `animation-vocabulary` | `emilkowalski/skills`                      | Emil Kowalski  |
| `apple-design`         | `emilkowalski/skills`                      | Emil Kowalski  |
| `emil-design-eng`      | `emilkowalski/skills`                      | Emil Kowalski  |
| `review-animations`    | `emilkowalski/skills`                      | Emil Kowalski  |
| `swiftui-pro`          | `twostraws/swiftui-agent-skill`            | Paul Hudson    |

These are committed snapshots so a clone is reproducible, but they are not maintained or claimed as original work
here. Do not edit them directly. Run `npm run skills:update`, review both the snapshot and lockfile changes, and then
run `npm run verify`.

## Configured Superpowers fork

[`pdugan20/superpowers`](https://github.com/pdugan20/superpowers) is a thin fork of
[`obra/superpowers`](https://github.com/obra/superpowers). It is installed as
`superpowers@superpowers-configured` in both products. `config/superpowers.json` records the exact upstream baseline,
fork version, policy patch set, and invocation classification.

The fork changes only policy and presentation:

- it disables the automatic session-start `using-superpowers` injection;
- it makes strict orchestration workflows explicit-only in both Codex and Claude; and
- it removes the brainstorming Visual Companion/browser option picker.

Strict workflows:

| Superpowers skill                | Invocation policy |
| -------------------------------- | ----------------- |
| `brainstorming`                  | Explicit-only     |
| `dispatching-parallel-agents`    | Explicit-only     |
| `executing-plans`                | Explicit-only     |
| `finishing-a-development-branch` | Explicit-only     |
| `subagent-driven-development`    | Explicit-only     |
| `test-driven-development`        | Explicit-only     |
| `using-git-worktrees`            | Explicit-only     |
| `using-superpowers`              | Explicit-only     |
| `writing-plans`                  | Explicit-only     |

The fork's review, debugging, verification, and skill-authoring skills can still be selected automatically when
relevant. Invoke strict skills as `$superpowers:<skill-name>` in Codex or `/superpowers:<skill-name>` in Claude.

## Desired user-managed Codex plugins

`config/codex-plugins.txt` is the machine-readable desired-state manifest:

- `superpowers@superpowers-configured`
- `firebase@firebase`
- `cloudflare@cloudflare`
- `mintlify@claude-plugins-official`
- `mintlify-docs@pdugan20-plugins`
- `figma@openai-curated`
- `github@openai-curated`
- `sentry@openai-curated`
- `expo@openai-curated`
- `vercel@openai-curated`

Each plugin may contribute many skills or MCP tools. Do not duplicate those transitive skill names here because they change with plugin versions. Use `codex plugin list --json` for exact installed versions and the Codex skill picker for the current transitive skill inventory.

`mintlify-docs` is Patrick's maintained four-skill docs-site plugin. Its source remains
[`pdugan20/mintlify-docs`](https://github.com/pdugan20/mintlify-docs); this repository records the desired installation
without copying its skills. The official `mintlify` plugin remains installed alongside it for component and
`docs.json` mechanics.

## Codex runtime-managed plugins

The Codex/ChatGPT installation currently provides these additional enabled bundles. They are updated with the application or its primary runtime rather than pinned in the personal plugin manifest:

- Primary runtime: `documents`, `pdf`, `spreadsheets`, `presentations`, `template-creator`
- Bundled desktop capabilities: `sites`, `browser`, `computer-use`, `visualize`
- Remote Product Design skills: useful focused skills remain available, while `product-design:index` and `product-design:ideate` are disabled by `configure-codex.py`
- System skills such as `openai-docs`, `skill-creator`, `plugin-creator`, `skill-installer`, and `imagegen`

Generated-image ideation is opt-in. Code-native UI ideation in the actual browser or simulator is the default.

## Desired Claude plugins

`config/claude-plugins.txt` records the user-scoped Claude plugin set currently preserved for compatibility:

- `claude-code-setup`
- `code-review`
- `code-simplifier`
- `commit-commands`
- `explanatory-output-style`
- `feature-dev`
- `frontend-design`
- `mintlify-docs@pdugan20-plugins`
- `skill-creator`
- `swift-lsp`
- `typescript-lsp`
- `superpowers@superpowers-configured`

`configure-claude.py` enables the configured fork and disables `superpowers@claude-plugins-official` so only the
policy-controlled copy is active. Disabled, project-local, and historical Claude plugins are not part of the desired
setup unless added to `config/claude-plugins.txt`.

## What does not sync through Git

- Codex, Claude, GitHub, Figma, Firebase, Sentry, and other OAuth sessions
- API keys and provider credentials
- macOS Accessibility and Screen Recording permissions
- Xcode simulators, certificates, provisioning, and command-line tools
- Node, Ruby, Python, Homebrew, Firebase CLI, and other development toolchains
- Trusted-workspace decisions, Codex task history, memory, caches, and most desktop preferences
- Repository working trees and any uncommitted changes

Keep credentials and personal data out of this repository.

## Live inventory commands

```bash
codex plugin list --json
codex plugin marketplace list
claude plugin list --json
./scripts/verify-setup.sh
npm run catalog:snapshot
```

The browser catalog derives its canonical view from this repository. `npm run catalog:snapshot` creates an ignored
machine-local snapshot for the **This Mac** view; it never becomes a portable source of truth.

See `inventory/maintenance.md` for upgrades and upstream Superpowers review. See `README.md` for new-machine setup.
