# Agent tooling manifest

This is the authoritative map of Patrick's shared Claude and Codex setup. The private Git repository at `pdugan20/agent-tooling` is the canonical source; runtime caches and settings under the home directory are generated machine state.

## Canonical sources

| Concern                      | Canonical source              | Runtime destination                                             |
| ---------------------------- | ----------------------------- | --------------------------------------------------------------- |
| Global working agreement     | `global/AGENTS.md`            | `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`                  |
| Portable personal skills     | `skills/*/SKILL.md`           | `~/.agents/skills/*` and `~/.claude/skills/*`                   |
| Production delivery plugin   | `plugins/patrick-delivery/`   | Codex plugin cache and `~/.claude/skills/*` compatibility links |
| Desired Codex plugins        | `config/codex-plugins.txt`    | `~/.codex/config.toml` and Codex plugin caches                  |
| Desired Claude plugins       | `config/claude-plugins.txt`   | `~/.claude/settings.json` and Claude plugin caches              |
| Codex machine policy         | `scripts/configure-codex.py`  | `~/.codex/config.toml`                                          |
| Claude machine policy        | `scripts/configure-claude.py` | `~/.claude/settings.json`                                       |
| Repository-specific guidance | Each repository's `AGENTS.md` | Travels with that repository                                    |

Do not edit generated runtime cache files. Edit this repository, rerun the setup scripts, and start a new task.

## Owned skills

Portable skills shared directly by Codex and Claude:

- `animation-vocabulary`
- `apple-design`
- `code-native-ui-ideation`
- `emil-design-eng`
- `review-animations`
- `swiftui-pro`

Skills in `patrick-delivery`:

| Skill                  | Invocation policy                                                |
| ---------------------- | ---------------------------------------------------------------- |
| `feature-delivery`     | Automatic only for substantial production feature implementation |
| `formal-spec`          | Explicit-only                                                    |
| `strict-tdd`           | Explicit-only                                                    |
| `write-plan`           | Explicit-only                                                    |
| `execute-plan`         | Explicit-only                                                    |
| `production-hardening` | Explicit-only                                                    |

Patrick Delivery currently uses manifest version `0.2.0`. This plugin version is independent from the repository
version in `package.json`; bump it only when plugin behavior or compatibility changes.

In Codex, delivery skills use the `$patrick-delivery:<skill>` namespace. Claude receives direct personal-skill links such as `/strict-tdd` and `/feature-delivery`.

## Desired user-managed Codex plugins

`config/codex-plugins.txt` is the machine-readable desired-state manifest:

- `patrick-delivery@personal`
- `firebase@firebase`
- `cloudflare@cloudflare`
- `mintlify@claude-plugins-official`
- `figma@openai-curated`
- `github@openai-curated`
- `sentry@openai-curated`
- `expo@openai-curated`
- `vercel@openai-curated`

Each plugin may contribute many skills or MCP tools. Do not duplicate those transitive skill names here because they change with plugin versions. Use `codex plugin list --json` for exact installed versions and the Codex skill picker for the current transitive skill inventory.

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
- `skill-creator`
- `swift-lsp`
- `typescript-lsp`

Superpowers may remain installed in Claude's cache, but `configure-claude.py` forces it disabled. Disabled, project-local, and historical Claude plugins are not part of the desired setup unless added to `config/claude-plugins.txt`.

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
