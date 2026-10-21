# Set up agent tooling

For Patrick or a maintainer applying the selected setup to a Mac. Codex is the primary harness; use Claude Code
when its native harness is useful. Selecting a Claude model through a provider does not select the Claude Code setup.

## Current command boundary

The default commands configure Codex. Claude Code has an independent, explicit setup path:

| Command | Behavior |
| --- | --- |
| `npm run setup` | Bootstraps Codex, installs its selected CLI plugins, and verifies Codex |
| `npm run bootstrap` | Links Codex instructions and shared skills; applies selected Codex settings |
| `npm run setup:check` | Checks Codex links, CLI plugins, skill overrides, and selected MCP configuration |
| `npm run setup:claude` | Installs Claude's TypeScript language server if missing, bootstraps Claude, installs its selected plugins, and verifies Claude |
| `npm run bootstrap:claude` | Links instructions, skills, and output styles into the active Claude profile; configures its settings and context hook |
| `npm run setup:check:claude` | Checks the active Claude profile, selected plugins, and language servers |
| `npm run plugins:refresh:codex` | Refreshes the CLI-managed Codex plugin set and reapplies Codex configuration fixes |
| `npm run plugins:refresh:claude` | Refreshes only the selected optional Claude plugins |
| `npm run mcp:check` | Compares CLI-visible MCP authentication state with the repository's authentication policy |
| `npm run verify` | Checks repository content; does not verify the signed-in desktop session |

Using a Claude model through a Codex provider requires only the Codex path. Optional Claude commands do not run
Codex setup. Codex setup, bootstrap, and checks honor `CODEX_HOME`, falling back to `~/.codex`; shared user skills use `~/.agents/skills`.

## Apply the Codex setup

Prerequisites:

- macOS, Node.js from [`.nvmrc`](../.nvmrc), and Python 3; [`.python-version`](../.python-version) records the repository baseline.
- Codex CLI with `plugin` and `plugin marketplace` commands, and GitHub CLI.
- Existing CLI sign-ins and access to the configured marketplaces.

From your chosen checkout location:

```bash
gh repo clone pdugan20/agent-tooling
cd agent-tooling
npm run setup
```

The scripts resolve this checkout from their own location. They refuse to replace existing non-matching instruction
or skill paths. Compare an existing copy with the canonical source before moving it aside; preserve divergent work.

Start a fresh Codex chat afterward. Review the entries in
[`config/codex-managed-plugins.txt`](../config/codex-managed-plugins.txt) in the desktop Plugins interface and complete
required connector authentication. Product sign-ins, secrets, permissions, and developer toolchains remain local.

Successful installation ends with `codex setup verified.` and `codex setup is complete.`
Use `npm run mcp:check` separately after connector authentication; a reported blocker is policy, not a live proof
that an upstream bug still exists.

Setup preserves extra skills, plugin installations, marketplaces, and unrelated settings. It does not remove legacy
links or reconcile undeclared plugins. Conflicting selected links stop bootstrap; inspect and preserve the existing
path before resolving ownership. Checks require the selected plugins and configured Superpowers baseline; a conflict
can stop configuration or fail verification without removing anything. Setup is not transactional: earlier successful additions remain
if a later step fails. Rerun after resolving the reported conflict.

Refresh also preserves unselected plugins and marketplaces. It updates marketplace snapshots by selected name,
refreshes the selected plugin IDs, and reapplies that harness's settings. Retiring old entries requires a separate
review of their owners; no setup or refresh command removes them automatically.

## Use optional Claude Code support

Install Claude Code separately, with Xcode or a Swift toolchain providing `sourcekit-lsp`. Then run:

```bash
npm run setup:claude
```

This path installs the TypeScript language server through npm if missing. It leaves Codex configuration and user
skill links alone. Reapply links/settings with `npm run bootstrap:claude`; check with `npm run setup:check:claude`.
Restart Claude Code after setup.

Claude paths honor `CLAUDE_CONFIG_DIR` when set and otherwise use `~/.claude`. Its bootstrap links the shared agreement
as `CLAUDE.md`, links the selected skills, selects the [output style](output-styles.md), and registers the
repository-context hook. That hook checks whether Claude loads `AGENTS.md` natively before supplying fallback context.

Claude's `swift-lsp` and `typescript-lsp` plugins are harness-specific. Their declarations do not add language-server
tools to Codex. See [plugin compatibility](architecture.md#plugins-and-compatibility).

## Browse the catalog

```bash
npm ci
npm run catalog
```

The development server binds to `127.0.0.1:4173` with route `/catalog/`; it is loopback-only by default.
To compare installed state, run `npm run catalog:snapshot`, open `/catalog/?runtime=local`, and choose **This Mac**.
The generated `catalog/runtime-data.local.json` is ignored by Git.

To include canonical skills from immediate child primary repositories, pass your repository collection directory:

```bash
npm run catalog:snapshot -- --repos-root /path/to/repositories
```

Replace `/path/to/repositories` with that directory. Linked worktrees are skipped. Project skills remain owned by
their projects. User skill scans cover `~/.agents/skills`, the active Codex home's `skills` folder, and the active
Claude profile's `skills` folder. Links resolving to the same entrypoint share a row; different files with the same
name remain separate. External entries are observations, not additions to the selected inventory.

The local snapshot also summarizes configuration presence and MCP/hook/skill-override counts without copying
commands, URLs, environment values, or credentials. Missing CLI inventories produce notices rather than hiding
observed skills. Expand **Snapshot coverage** for those notices. System/admin skills, plugin skill trees, nested
project skill directories, and effective project or managed policy remain outside the scan.

Skill details distinguish declared Codex and Claude invocation policies and show observed local overrides. Automatic
eligibility is not a promise that a runtime will invoke the skill, and file presence does not prove session availability.
Use the [machine audit checklist](maintenance.md#audit-a-machine) when reconciling a whole machine.

## Develop this repository

Install Node.js from `.nvmrc`, Python 3, and these verification tools:

```bash
nvm use
npm ci
python3 -m pip install pre-commit==4.6.1
brew install actionlint gitleaks lychee typos-cli zizmor
pre-commit install --hook-type pre-commit --hook-type pre-push
npm run verify
```

Use a Python environment if the system Python refuses package installation. The `ci` job uses the same verification
entry point. External link checks run separately on a schedule. See [quality tooling](quality-tooling.md).

## Troubleshoot setup

- **A link already exists:** compare its target and contents; bootstrap will not replace it automatically.
- **A capability is missing:** inspect its delivery source, selected profile, and current chat's available tools and skills.
  A downloaded cache or catalog row does not prove that the active chat can use it.
- **CLI and desktop disagree:** check the versions and binary paths independently. The shell's `codex` can differ
  from the desktop runtime, and CLI inventory is not a complete account or workspace inventory.
- **A config change seems ignored:** check trusted project overrides and the active profile, then start a new chat.
  See [Codex configuration layers](architecture.md#instructions-and-configuration).

For account, provider, or OpenCodex problems, follow the private-note routing in the shared working agreement.
Keep machine-specific recovery steps and account observations outside this repository.
