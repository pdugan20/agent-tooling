# Agent Tooling

[![CI](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml/badge.svg)](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/pdugan20/agent-tooling?logo=github)](https://github.com/pdugan20/agent-tooling/releases)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D22.22.2-339933?logo=node.js&logoColor=white)](https://nodejs.org/)

Portable, canonical tooling shared across Codex and Claude Code projects: working agreements, reusable workflows, a
reconciled plugin inventory, and machine setup.

## Quick start

Install and authenticate Codex, Claude Code, and GitHub CLI, then run:

```bash
gh repo clone pdugan20/agent-tooling
cd agent-tooling
npm run setup
```

The checkout can live anywhere. Setup scripts resolve the repository from their own location and do not require a
particular parent directory or repository collection layout.

If `CLAUDE_CONFIG_DIR` is set, setup, refresh, and verification use that active Claude profile instead of
`~/.claude`. Existing non-symlink instruction or skill paths are never replaced automatically.

The setup uses Xcode's bundled `sourcekit-lsp` for Claude's Swift code intelligence and installs the TypeScript
language server required by Claude's TypeScript plugin. Codex does not currently load Claude's LSP plugin component;
it continues to use project builds, type checks, linters, tests, and editor context for those languages.

Restart Codex and Claude afterward. Product OAuth sessions, API keys, local toolchains, and repository-specific
instructions remain machine- or project-local.

The setup script installs only marketplace-managed Codex plugins. After signing in, open the Codex Plugins tab and
confirm the entries in [`config/codex-managed-plugins.txt`](config/codex-managed-plugins.txt); Codex owns and updates
that separate account/workspace layer.

## Included

| Area                   | Purpose                                                  | Canonical source                                      |
| ---------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| Shared instructions    | Exploration, production, Firebase, and safety policy     | [`global/AGENTS.md`](global/AGENTS.md)                |
| Local workflows        | Instructions maintained as part of this repository      | [`skills/`](skills/)                                  |
| Upstream skills        | Official CLI-managed snapshots with source provenance   | [`.agents/skills/`](.agents/skills/), `skills-lock.json` |
| Plugin setup           | Marketplace-installed and Codex-managed plugin sets      | [`config/`](config/)                                  |
| Machine setup          | Bootstrap, refresh, configuration, and verification      | [`scripts/`](scripts/)                                |

The top-level [`skills/`](skills/) directory intentionally contains only the three workflows maintained here. The
seven third-party skills are installed into this repository by the official `skills` CLI, committed under
[`.agents/skills/`](.agents/skills/), and tracked by `skills-lock.json`. That is their **management scope**. Bootstrap
links all ten canonical skills into each agent's home-directory skill location, so their **runtime availability** is
global across repositories. Do not edit upstream snapshots by hand; use `npm run skills:update` and review the diff.

## Catalog

Browse the canonical setup in a searchable local web catalog:

```bash
npm run catalog
```

Open [localhost:4173/catalog/](http://127.0.0.1:4173/catalog/). To compare the repository with installed plugins and
skills on the current Mac, run `npm run catalog:snapshot`, reopen the catalog with `?runtime=local`, and choose
**This Mac**. The snapshot is machine-local and ignored by Git.

To include repository-scoped skills from a folder of Git checkouts without hardcoding that folder into the setup,
pass it when creating the local snapshot:

```bash
npm run catalog:snapshot -- --repos-root /path/to/repositories
```

The scanner reads only immediate child primary repositories and their canonical `.agents/skills` metadata. Linked
worktrees are skipped so the catalog does not repeat the same project profile. It does not copy project skills into
`agent-tooling` or make them global.

The catalog labels effective availability separately from ownership and source. “All repositories” describes where
the capability can run; it does not mean its canonical source is stored globally or updated outside this repository.
Source names link to the canonical GitHub skill or plugin when the publisher exposes one.

Plugins are grouped by logical capability. When Codex and Claude use different package IDs for the same capability,
the catalog shows one row with separate installation details for each app. Summary counts therefore count
capabilities, not package records.

## Common commands

| Command                          | Purpose                                            |
| -------------------------------- | -------------------------------------------------- |
| `npm run setup`                  | Configure the complete setup on a new machine      |
| `npm run bootstrap`              | Reapply shared links and non-secret runtime policy |
| `npm run plugins:refresh:codex`  | Refresh the desired Codex plugin set               |
| `npm run plugins:refresh:claude` | Refresh the desired Claude plugin set              |
| `npm run setup:check`            | Compare this Mac with the desired setup            |
| `npm run mcp:check`              | Check machine-local Codex MCP authentication       |
| `npm run skills:update`          | Check and apply upstream skill updates for review  |
| `npm run catalog`                | Generate and serve the browser catalog             |
| `npm run verify`                 | Run the complete local and GitHub Actions gate     |

`npm run` commands are the supported user-facing interface. They delegate to the scripts in [`scripts/`](scripts/)
so documentation and automation share memorable, stable command names while the implementation can evolve.

## Development

```bash
nvm use
npm ci
python3 -m pip install pre-commit==4.6.1
brew install actionlint gitleaks
pre-commit install --hook-type pre-commit --hook-type pre-push
npm run verify
```

The `ci` job is the stable required check. Verification covers unit tests, skill validation, Markdown and formatting,
Python and shell quality, workflow syntax, catalog drift, repository policy, full-history secret scanning, and
whitespace.

## Documentation

- [Manifest](inventory/manifest.md): ownership, runtime mapping, and what does not sync.
- [Scope guide](inventory/scope.md): which capabilities are global, which stay with projects, and why.
- [Maintenance](inventory/maintenance.md): updates, plugin refreshes, Superpowers review, and releases.
- [Authoring checks](inventory/authoring.md): linting, formatting, validation, and behavioral testing for skills and plugins.
- [Outstanding work](inventory/next-steps.md): the remaining authentication-dependent and MacBook setup tasks.
- [Migration record](inventory/publication.md): completed cross-repository rollout.
- [Repository inventory](inventory/repos.md): repositories governed by the shared setup.
- [Changelog](CHANGELOG.md): curated repository releases and upgrade notes.

## Releases

Repository releases use `vMAJOR.MINOR.PATCH` tags and curated notes from `CHANGELOG.md`. See the
[maintenance guide](inventory/maintenance.md#release-agent-tooling) for the release workflow and component-specific
update procedures.
