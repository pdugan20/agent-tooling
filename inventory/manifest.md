# Agent tooling manifest

This is the authoritative map of Patrick's shared Claude and Codex setup. The public Git repository at
`pdugan20/agent-tooling` is the canonical source; runtime caches and settings under the home directory are generated
machine state.

## Canonical sources

| Concern                      | Canonical source                             | Runtime destination                                |
| ---------------------------- | -------------------------------------------- | -------------------------------------------------- |
| Global working agreement     | `global/AGENTS.md`                           | `~/.codex/AGENTS.md` and `$CLAUDE_CONFIG_DIR/CLAUDE.md` |
| Locally maintained workflows | `skills/*/SKILL.md`                          | `~/.agents/skills/*` and `$CLAUDE_CONFIG_DIR/skills/*`  |
| Locked upstream skills       | `.agents/skills/*` and `skills-lock.json`    | `~/.agents/skills/*` and `$CLAUDE_CONFIG_DIR/skills/*`  |
| Configured Superpowers state | `config/superpowers.json`                    | Fork repository and both products' plugin caches   |
| Marketplace-installed Codex plugins | `config/codex-plugins.txt`            | `~/.codex/config.toml` and Codex plugin caches     |
| Codex-managed plugins        | `config/codex-managed-plugins.txt`           | Codex account/workspace and Plugins tab            |
| Desired Claude plugins       | `config/claude-plugins.txt`                  | `$CLAUDE_CONFIG_DIR/settings.json` and Claude plugin caches |
| Personal plugin marketplace  | `pdugan20/pdugan20-plugins`                  | Both products' marketplace snapshots               |
| Codex machine policy         | `scripts/configure-codex.py`                 | `~/.codex/config.toml`                              |
| Claude machine policy        | `scripts/configure-claude.py`                | `$CLAUDE_CONFIG_DIR/settings.json`                  |
| Repository-specific guidance | Each repository's `AGENTS.md`                | Travels with that repository                       |

Do not edit generated runtime cache files. Edit this repository, rerun the setup scripts, and start a new task.

## Scope model

Scope has three independent meanings:

- **Management scope** identifies the Git repository and lockfile that own an artifact's canonical source.
- **Runtime availability** identifies whether the artifact can run in every repository or only a particular project.
- **Persistence scope** identifies whether a setting is shared through Git, stored for one user, or kept only in a
  machine-local settings file.

`$CLAUDE_CONFIG_DIR` in this table means the active Claude profile, with `~/.claude` used when the variable is unset.

The official `skills` CLI reports the locked upstream collection as project-scoped because `agent-tooling` owns its
snapshots and lockfile. `bootstrap.sh` then links every canonical skill into `~/.agents/skills` and the active Claude
profile's `skills` directory, making those skills globally available at runtime. Repository-specific skills instead
live in that repository's `.agents/skills`, with Claude compatibility links in `.claude/skills`. Machine-only plugin
choices belong in the active profile's `settings.local.json` and do not sync.

See [`scope.md`](scope.md) for the audited global profile, project profiles, and placement rules.

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
| `find-animation-opportunities` | `emilkowalski/skills`              | Emil Kowalski  |
| `pick-ui-library`      | `emilkowalski/skills`                      | Emil Kowalski  |
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

## Marketplace-installed Codex plugins

`config/codex-plugins.txt` is the machine-readable desired-state manifest:

- `superpowers@superpowers-configured`
- `firebase@firebase`
- `cloudflare@cloudflare`
- `mintlify@mintlify-marketplace`
- `mintlify-docs@pdugan20-plugins`
- `sentry@claude-plugins-official`
- `expo@claude-plugins-official`

Each plugin may contribute many skills or MCP tools. Do not duplicate those transitive skill names here because they change with plugin versions. Use `codex plugin list --json` for exact installed versions and the Codex skill picker for the current transitive skill inventory.

`mintlify-docs` is Patrick's maintained four-skill docs-site plugin. Its source remains
[`pdugan20/mintlify-docs`](https://github.com/pdugan20/mintlify-docs); this repository records the desired installation
without copying its skills. The official `mintlify` plugin remains installed alongside it for component and
`docs.json` mechanics, sourced from Mintlify's own Git marketplace rather than a stale third-party pin.

Plugin sourcing is decided capability by capability. Expo and Sentry use current vendor packages because their
former Codex-managed copies were materially behind and supplied no unique connected app.

## Codex-managed plugins

`config/codex-managed-plugins.txt` records plugins intentionally installed from the Codex Plugins tab. Codex updates
and injects these through the signed-in account/workspace layer; `codex plugin list` does not reliably report that
state, and the setup scripts must not attempt to install a second CLI copy.

Figma, GitHub, and Vercel remain Codex-managed: Figma carries Codex tool-schema compatibility changes, GitHub supplies
the connected repository app, and Vercel exposes broader deployment and project operations without the direct
plugin's session hooks or default-on telemetry. Data Analytics, OpenAI Developers, Product Design, and Slack are also
recorded here because they are intentionally available through the same account-managed layer. Verify this file
against the Plugins tab after signing in on a new machine.

## Codex runtime-managed plugins

The Codex/ChatGPT installation currently provides these additional enabled bundles. They are updated with the application or its primary runtime rather than pinned in the personal plugin manifest:

- Primary runtime: `documents`, `pdf`, `spreadsheets`, `presentations`, `template-creator`
- Bundled desktop capabilities: `sites`, `browser`, `computer-use`, `visualize`
- Remote Product Design skills: useful focused skills remain available, while `product-design:index` and `product-design:ideate` are disabled by `configure-codex.py`
- System skills such as `openai-docs`, `skill-creator`, `plugin-creator`, `skill-installer`, and `imagegen`

Generated-image ideation is opt-in. Code-native UI ideation in the actual browser or simulator is the default.

## Desired Claude plugins

`config/claude-plugins.txt` is the machine-readable desired state for enabled user-scoped Claude plugins. It includes:

- shared service capabilities: Cloudflare, Expo, Figma, Firebase, GitHub, Mintlify, Mintlify Docs, Sentry, Supabase,
  and Vercel;
- general Claude workflows: Claude Code Setup, Code Review, Code Simplifier, Commit Commands, Feature Development,
  Frontend Design, Plugin Development, and Skill Creator;
- the configured Superpowers fork and Claude-only Swift and TypeScript LSP integrations.

The exact package IDs remain in the manifest. Shared logical capabilities can have different app-specific package
IDs—for example, Codex uses `firebase@firebase` while Claude uses `firebase@claude-plugins-official`. The catalog
groups those records into one Firebase row and shows both installations underneath it.

`configure-claude.py` enables the configured fork and disables `superpowers@claude-plugins-official` so only the
policy-controlled copy is active. Disabled, project-local, and historical Claude plugins are not part of the desired
setup unless added to `config/claude-plugins.txt`.

Playwright is intentionally excluded because browser automation is not part of the desired Claude profile. Railway
is also excluded globally: `rss-feed-generator` pins Railway's canonical `use-railway` skill in the project for both
agents. `npm run setup:check` reports any enabled user plugin that is missing from the manifest instead of silently
accepting local drift.

`explanatory-output-style` is intentionally excluded: its SessionStart hook adds mandatory educational “Insight”
blocks to every task, increasing verbosity and token use during lightweight iteration without adding tools.

### Claude-only language servers

`swift-lsp` and `typescript-lsp` are intentionally Claude-only plugins. Claude Code supports an `lspServers`
component that connects its built-in LSP tool to separately installed language-server binaries. `swift-lsp` uses
Xcode or Swift's `sourcekit-lsp`; `typescript-lsp` uses the globally installed `typescript-language-server` and
`typescript` packages. `npm run setup` installs the TypeScript prerequisites, and `npm run setup:check` checks both
binaries.

Codex's current plugin format does not define an LSP-server component, so installing these Claude plugins through a
Codex marketplace would create an installed record without giving Codex Claude's diagnostics or navigation tool.
Keep them out of `config/codex-plugins.txt`. In Codex, rely on the repository's compiler, type checker, linter, tests,
and available editor context; reassess only if OpenAI publishes an LSP plugin component.

- [Claude Code LSP plugin reference](https://code.claude.com/docs/en/plugins-reference#lsp-servers)
- [Codex plugin structure](https://developers.openai.com/plugins/build/plugins#plugin-structure)

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
npm run setup:check
npm run mcp:check
npm run catalog:snapshot
```

The browser catalog derives its canonical view from this repository. `npm run catalog:snapshot` creates an ignored
machine-local snapshot for the **This Mac** view; it never becomes a portable source of truth.

See `inventory/maintenance.md` for upgrades and upstream Superpowers review. See `README.md` for new-machine setup.
