# Architecture and scope

`agent-tooling` owns Patrick's selected agent configuration. Codex is the primary harness; Claude Code support is
optional. The [setup guide](setup.md) documents the default Codex commands and explicit Claude commands.

## Ownership

| Concern | Canonical source | Runtime destination |
| --- | --- | --- |
| Shared working agreement | `global/AGENTS.md` | `~/.codex/AGENTS.md` and the active Claude profile |
| Patrick-owned skill content | [Skills](https://github.com/pdugan20/skills) releases | Locked snapshots selected here |
| Selected standalone skills | `.agents/skills/*` and `skills-lock.json` | User-level skill links |
| CLI-managed Codex plugin selection | `config/codex-plugins.txt` | Configured marketplaces and installed plugins |
| Desired desktop-managed plugins | `config/codex-managed-plugins.txt` | Signed-in account or workspace plugin state |
| Selected standalone Codex MCP servers | `config/codex-mcp-servers.json` | Named tables in `~/.codex/config.toml` |
| Optional Claude plugins and settings | `config/claude-plugins.txt`, `scripts/configure-claude.py` | Active Claude profile |
| Configured Superpowers baseline | `config/superpowers.json` | Maintained fork and installed plugin |
| Project behavior | Each project's `AGENTS.md` and local configuration | That project |
| Selected-capability catalog | Generated `catalog/data.json` | Local browser catalog |

Edit managed sources here and Patrick-owned skills in Skills. Preserve settings owned by the user, an application,
a provider, another repository, or an administrator. This repository owns a subset of a machine's configuration.

## Model, harness, and provider

The model generates responses. The harness supplies instructions, skill discovery, tools, permissions, and session
behavior. A provider or proxy routes model requests. These are separate choices.

Using Claude through Codex does not make Claude Code's settings, slash commands, output styles, or language-server
plugins active. OpenCodex documents its [Codex integration](https://opencodex.me/guides/codex-integration/) separately
from model routing. Keep accounts, proxy lifecycle, and machine recovery in private local notes.

## Instructions and configuration

Codex natively loads global `AGENTS.md` guidance and project instructions from the project root down to the working
directory. `AGENTS.override.md` takes precedence at its directory level. This repo configures `CLAUDE.md` as a
fallback when the normal instruction names are absent; it is a compatibility choice, not a requirement for new projects.
Read nested instructions before editing below the working directory.
[Official instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

User configuration, trusted project `.codex/config.toml` files, command overrides, and managed policies can all
affect the result. A user config file alone does not establish effective settings. Project trust controls whether
project `.codex/` configuration loads; enforced organizational requirements constrain local choices.
[Official configuration layers](https://learn.chatgpt.com/docs/config-file/config-basic)

The repository's Codex configurator manages the instruction fallback, selected skill overrides, a legacy
computer-use command repair, and the named MCP manifest entries. It preserves unrelated configuration, including
provider routing. Its legacy repair is not a recommendation to install a separate computer-use server.

## Skill ownership and discovery

The Skills CLI installs selected snapshots under `.agents/skills/` and records provenance in `skills-lock.json`.
Default bootstrap links them into `~/.agents/skills` for Codex. `bootstrap:claude` links them into the active Claude skill directory. `.claude/skills/`
entries in this repository are compatibility links.

Codex supports repository and user `.agents/skills` directories, symlinked folders, and runtime-supplied skills.
A machine can also contain legacy skill locations and plugin-bundled skills. The current chat's available-skills
catalog is the evidence for what the agent can invoke. Duplicate names do not imply merged contents.
[Official skill discovery](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)

Do not edit locked snapshots. Release first-party changes upstream, install the reviewed release here, and inspect
the diff. Skills linked directly from another checkout follow that checkout and need their own ownership and update
policy. A globally available skill is not necessarily managed by this repository.

Management scope, runtime availability, and persistence are independent. A snapshot managed here can run globally;
a project-owned skill can remain local; account-managed plugins can follow a sign-in without being locked here.
See [invocation policy](skill-invocation.md) for automatic and explicit use.

## Plugins and compatibility

Plugins distribute skills, MCP connections, and supported runtime extensions. Current OpenAI documentation prefers
portable root `plugin.json` manifests with OpenAI-specific settings under `extensions.com.openai`.
The `.codex-plugin/plugin.json` compatibility layout remains supported. Existing upstream packages need not be
rewritten merely to match the newer layout. [Official packaging guidance](https://developers.openai.com/plugins/build/plugins)

Local or Git marketplaces, the public plugin directory, workspace installations, and runtime bundles have different
management paths. This repo's CLI and desktop manifests describe its chosen maintenance split; they are not an
exhaustive taxonomy of Codex. Local enablement settings do not replace workspace installation policy.

Codex supports lifecycle hooks, including hooks bundled with manually installed desktop plugins. Non-managed hooks
require review and trust of their current definitions; public-directory submission has additional restrictions.
Do not infer hook activation from plugin installation. [Official hooks guidance](https://learn.chatgpt.com/docs/hooks)

Claude's `outputStyles` and `lspServers` declarations are not equivalent Codex components. Skills and MCP capabilities
can be reused where supported, but each package needs a compatibility review. An Anthropic marketplace name alone
does not make a package Claude-only. [Official migration guidance](https://developers.openai.com/plugins/guides/submit-claude-plugin)

Use only the configured Superpowers fork. Its invocation groups and policy patches live in `config/superpowers.json`.
Strict planning, TDD, worktrees, orchestration, and image generation retain the opt-in boundaries in `global/AGENTS.md`.

## Standalone MCP servers

`config/codex-mcp-servers.json` pins standalone servers that should survive setup. The configurator converges those
named tables and preserves unrelated servers and authentication. Plugin-provided tools and other local servers
have separate owners.

The XcodeBuildMCP selection enables Simulator, semantic UI automation, and debugging with telemetry disabled.
Its exact package version and environment live in the manifest. Computer use supplies visual judgment; Instruments
or `xctrace` and suitable device evidence support performance claims.

The CircleCI server runs through the installed CLI (`circleci mcp start`) with an `enabled_tools` allowlist of read-only
tools: jobs, step output, workflows, pipelines, runs, test results, artifacts, config validation, and project, orb,
and resource-usage reads. Secret, environment-variable, trigger, rerun, cancel, approval, rollback, and generic API
tools stay out of agent sessions; use the CLI or web app directly for those.

## Catalog and persistence

The catalog records selected skills and plugins, grouping equivalent package IDs under a logical capability.
Its local snapshot observes user skill entrypoints, CLI plugins, and configuration counts; it can also scan project
skills. Resolved paths establish whether a skill link points to the selected source. Matching names alone do not
establish ownership, and distinct copies remain separate. Declared invocation is recorded independently for each
harness; local overrides are shown separately and do not establish effective session policy.

The local file stays ignored by Git. Configuration values and credentials are not copied into it. System/admin skills,
plugin skill trees, nested project directories, and effective project/managed configuration are outside its coverage.
Runtime bundles remain filtered from the plugin comparison. Inventory, effective availability, and usage differ.

Git carries this repo's selected configuration, locks, scripts, and docs. Accounts, credentials, permissions,
application caches, task history, other checkouts, and local customizations have separate persistence rules.
Use the [machine audit](maintenance.md#audit-a-machine) to find missing ownership before attempting cleanup.
Record retention and source decisions through the [capability ownership guide](capability-ownership.md).
