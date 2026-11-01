# Codex-first documentation audit

Reviewed 2026-10-20 for maintainers of this setup. This pass updates documentation and inventories ownership gaps;
it does not change setup scripts, selected capabilities, runtime configuration, or installed tooling.

## Findings and disposition

| Area | Finding | Disposition |
| --- | --- | --- |
| README | Setup internals, version notes, and catalog details obscured the entry point | Shortened; detailed instructions moved to `setup.md` and linked guides |
| Setup | Commands originally installed, configured, and checked both harnesses | Follow-up split defaults to Codex with explicit optional Claude targets |
| Architecture | Repo ownership was too easy to confuse with the full machine or runtime inventory | Separated model, harness, provider, selected configuration, and other owners |
| Skills | Codex supports symlink discovery, metadata policy, live skill discovery, and an initial context budget | Added current discovery and invocation guidance; kept snapshot ownership intact |
| Plugin packaging | Guidance omitted portable manifests and current lifecycle-hook support | Added supported portable and compatibility layouts, hook trust, and distribution boundaries |
| Claude compatibility | Writing-style mechanisms and visibility observations read too broadly | Scoped to Claude; historical measurements labeled separately from Codex controls |
| Plugin inventory | CLI, desktop, workspace, and cached state were treated too categorically | Documented the selected maintenance split and limits of each observation |
| Catalog | Snapshot originally checked only selected entrypoint names and mixed invocation policies | Added observed user skills, resolved-source identity, separate runtime policies, configuration counts, and explicit coverage notices |
| Validation | Maintenance claimed locked snapshots were excluded from lint policy despite whole-tree ClaudeLint validation | Corrected to match `package.json` and pre-commit behavior |
| Skill validation | `lint:claude` claimed strict skill-snapshot validation, but `validate-skills --path` validated nothing (2026-10-31) | Removed the no-op step; skill content is validated at its source and snapshots by the hash check |
| Dependency maintenance | Quality guide still attributed updates to Dependabot | Corrected to Renovate and its checked-in policy |

## Verification basis

Repository commands and behavior were checked against `package.json`, setup/configuration scripts, validators,
plugin and MCP manifests, catalog generation, and CI configuration. The README shape was compared with the local
Skills, Plugins, and Agent Workflows repositories. Machine-specific observations remain in a private local report.

Current official guidance was fetched for:

- [Instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and
  [configuration layers](https://learn.chatgpt.com/docs/config-file/config-basic).
- [Skill discovery, invocation, metadata, and overrides](https://learn.chatgpt.com/docs/build-skills).
- [Plugin packaging and marketplace operations](https://developers.openai.com/plugins/build/plugins) and
  [CLI plugin inventory](https://learn.chatgpt.com/docs/developer-commands#codex-plugin).
- [Lifecycle hooks and trust](https://learn.chatgpt.com/docs/hooks).
- [Claude plugin compatibility](https://developers.openai.com/plugins/guides/submit-claude-plugin).

A documented capability is not proof that a particular installed runtime, signed-in workspace, or current chat exposes
it. CLI help was checked independently of desktop runtime metadata. Installation and authentication were not rerun.

`npm run verify` passed with the repository Node.js version, including unit tests, lint, policy, catalog drift, and
secret scanning. A separate local-link check confirmed the README and guide targets and heading anchors.

## Setup implementation follow-up

The 2026-10-21 script update makes setup, bootstrap, and verification default to Codex. Explicit `:claude` targets
handle the optional harness, language server, settings, and hooks. Setup installation preserves existing extra plugins
and legacy links; maintenance refresh remains a separate command. Isolated-home tests cover harness boundaries,
provider settings, custom configuration directories, retained external links, and conflicting local files.

## Catalog and refresh follow-up

The next implementation batch expanded local snapshot coverage and made refresh preserve unselected installations.
It records declared invocation per runtime, keeps different copies with the same name separate, and reports missing
CLI inventories. Configuration summaries copy counts and presence rather than values. System/admin and plugin skill
trees, nested project scans, and effective runtime policy remain explicitly outside coverage. No installed skills
were moved or adopted. Neither refresh command runs plugin retirement or undeclared-plugin disabling.

## Deferred implementation

- Revalidate authentication policy entries and legacy compatibility repairs before changing them. A recorded upstream
  blocker or downloaded cache does not establish a current failure.

Use the [machine audit checklist](maintenance.md#audit-a-machine) before deciding what local tooling to adopt or retire.
The inventory does not authorize cleanup or turn existing machine customizations into portable defaults.

## Ownership follow-up

The 2026-10-21 reconciliation added the [ownership review ledger](capability-ownership.md) and product-scope tracking.
The selected lock remains unchanged. Broken user links were repaired with preserved
originals; machine bindings and repair evidence remain private. This follow-up is separate from the read-only
inventory and documentation pass above. Shared-workplace candidates remain evaluation records rather than plugin
additions, and asset-workflow dependencies are tracked with their product consumer.
