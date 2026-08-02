# Architecture and scope

`agent-tooling` is the canonical source for Patrick's shared Codex and Claude Code setup. Runtime caches and product
settings are generated machine state; edit this repository rather than patching installed copies.

## Sources of truth

| Concern | Canonical source | Runtime destination |
| --- | --- | --- |
| Shared working agreement | `global/AGENTS.md` | `~/.codex/AGENTS.md` and the active Claude profile |
| Patrick skills | `pdugan20/skills` releases | Skills CLI snapshots and user-level links |
| Managed skill snapshots | `.agents/skills/*` and `skills-lock.json` | User-level skill links for both products |
| Marketplace-installed Codex plugins | `config/codex-plugins.txt` | Codex configuration and plugin cache |
| Codex-managed plugins | `config/codex-managed-plugins.txt` | Signed-in Codex account/workspace |
| Managed Codex MCP servers | `config/codex-mcp-servers.json` | `~/.codex/config.toml` |
| Claude plugins | `config/claude-plugins.txt` | Claude user settings and plugin cache |
| Configured Superpowers policy | `config/superpowers.json` | The maintained fork and both plugin caches |
| Machine policy | `scripts/configure-codex.py` and `scripts/configure-claude.py` | Product settings files |
| Repository-specific behavior | The nearest repository `AGENTS.md` | Travels with that repository |
| Browsable inventory | Generated `catalog/data.json` | Local catalog and optional machine snapshot |

Text documentation explains the model but does not duplicate exact plugin or skill inventories. The config files,
lockfile, generated catalog, and installed-product listings are authoritative.

## Three kinds of scope

- **Management scope** identifies the repository and lockfile that own an artifact.
- **Runtime availability** identifies whether it can run in every repository or only one project.
- **Persistence scope** identifies whether it travels through Git, follows a signed-in account, or remains on one
  machine.

These are independent. The official `skills` CLI describes upstream snapshots as project-scoped because their
lockfile lives here, while `npm run bootstrap` links those same skills into both products' user-level skill folders.
Their effective runtime availability is therefore all repositories.

## Global or project-specific

| Put it in this shared setup when… | Put it in a project when… |
| --- | --- |
| Guidance should behave the same across most codebases. | It names project architecture, schemas, endpoints, commands, or release lanes. |
| It represents a reusable personal workflow or design method. | It must be versioned and reviewed with one application. |
| A plugin provides a broadly useful service integration. | Only that project needs or should pin the capability. |

Global does not mean always active. Invocation policy is separate: a global skill can be explicit-only, while a
project skill can trigger automatically when a request clearly matches it. Repository instructions should govern
local behavior without copying globally installed plugin files.

## Skills

The public [Skills](https://github.com/pdugan20/skills) repository is canonical for Patrick's
eleven design, UI-analysis, delivery, hardening, and documentation skills. This repository consumes its tagged
releases alongside seven third-party skills. All eighteen exact snapshots are installed by the
[`skills` CLI](https://github.com/vercel-labs/skills), stored under
`.agents/skills/`, and tracked by `skills-lock.json`. The `.claude/skills/` entries are compatibility links, not
separate copies.

Do not edit locked snapshots. Release first-party changes from Skills, install the new tag here, and
review the snapshot and lockfile diff. Run `npm run skills:update` for third-party updates. If a source needs local
policy, prefer runtime configuration or a clearly named addition to Skills over a silent fork.

## Managed Codex MCP servers

`config/codex-mcp-servers.json` is the exact, non-secret desired state for standalone Codex MCP servers that should
survive machine setup. `scripts/configure-codex.py` converges only those named tables in `~/.codex/config.toml` and
preserves unrelated servers and authentication state. `scripts/verify-setup.sh` checks the resulting configuration.

The initial XcodeBuildMCP entry is deliberately a Codex-only pilot. It pins the npm package and matching upstream
skill to v2.7.0, enables only Simulator, semantic UI automation, and debugging, and disables XcodeBuildMCP's Sentry
telemetry. Runtime log capture is part of the Simulator launch workflow; `logging` is not a current v2.7.0 workflow
name. Computer use remains the visual complement, and Instruments or `xctrace` remains the performance profiler.

Promote another standalone MCP into this manifest only when its behavior should be global, its command and version
can be pinned without secrets, setup can verify it, and a plugin or repository-local configuration is not the better
ownership boundary.

## Plugin layers

Codex has three plugin layers:

1. Marketplace-installed plugins managed by the scripts in this repository.
2. Plugins installed from the Codex Plugins tab and updated through the signed-in account/workspace.
3. Bundles supplied by the Codex application or primary runtime.

Claude plugins are installed at user scope from `config/claude-plugins.txt`. Claude paths use `$CLAUDE_CONFIG_DIR`
when set and otherwise default to `~/.claude`. The configured Superpowers fork is the only Superpowers installation
enabled in either product. Its exact version, upstream baseline, policy patches, and invocation groups live in
`config/superpowers.json` rather than duplicated prose.

The catalog groups different Codex and Claude package IDs under one stable logical capability ID. Each row retains
the per-product package, delivery method, version, and state, so grouping does not hide which installation supplies
the capability.

Generated-image ideation remains opt-in through `global/AGENTS.md` and Codex skill overrides. Code-native UI
exploration in the project browser or simulator is the default.

## Claude-only language servers

Claude Code supports plugin-provided `lspServers`; Codex's plugin format does not currently define an equivalent
component. Claude's Swift plugin uses Xcode or Swift's `sourcekit-lsp`, while its TypeScript plugin uses
`typescript-language-server`. `npm run setup` installs the TypeScript prerequisites and `npm run setup:check` verifies
both binaries.

Installing those Claude plugins through a Codex marketplace would create plugin state without supplying Claude's LSP
tool. Codex instead uses project builds, type checks, linters, tests, and editor context.

- [Claude Code LSP plugin reference](https://code.claude.com/docs/en/plugins-reference#lsp-servers)
- [Codex plugin structure](https://developers.openai.com/plugins/build/plugins#plugin-structure)

## Persistence across machines

Git carries the working agreement, maintained skills, locked upstream skills, plugin manifests, catalog, scripts,
and repository-specific instructions. A new machine applies them with `npm run setup`.

Git does not carry:

- OAuth sessions, API keys, provider credentials, or trusted-workspace decisions;
- macOS permissions, simulators, certificates, provisioning, or developer toolchains;
- installed product caches, task history, memory, or most desktop preferences; or
- working trees and uncommitted changes from other repositories.

Keep credentials and personal data out of this repository. Inspect the current machine without changing canonical
state with:

```bash
codex plugin list --json
codex plugin marketplace list
claude plugin list --json
npm run setup:check
npm run mcp:check
npm run catalog:snapshot
```

The generated **This Mac** catalog snapshot is ignored by Git and is never a portable source of truth.
