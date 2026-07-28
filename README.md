# Agent Tooling

[![CI](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml/badge.svg)](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/pdugan20/agent-tooling)](https://github.com/pdugan20/agent-tooling/releases/latest)
[![License](https://img.shields.io/github/license/pdugan20/agent-tooling)](LICENSE)
![Node](https://img.shields.io/badge/Node-22-3C873A?logo=nodedotjs&logoColor=white)

Portable, canonical tooling shared across Codex and Claude Code projects: working agreements, reusable workflows, a
policy-configured Superpowers fork, plugin manifests, and machine setup.

## Quick start

Install and authenticate Codex, Claude Code, and GitHub CLI, then run:

```bash
gh repo clone pdugan20/agent-tooling
cd agent-tooling
./scripts/setup-new-machine.sh
```

The checkout can live anywhere. Setup scripts resolve the repository from their own location and do not require a
particular parent directory or repository collection layout.

Restart Codex and Claude afterward. Product OAuth sessions, API keys, local toolchains, and repository-specific
instructions remain machine- or project-local.

## Included

| Area                   | Purpose                                                  | Canonical source                                      |
| ---------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| Shared instructions    | Exploration, production, Firebase, and safety policy     | [`global/AGENTS.md`](global/AGENTS.md)                |
| Local workflows        | Instructions maintained as part of this repository      | [`skills/`](skills/)                                  |
| Upstream skills        | Official CLI-managed snapshots with source provenance   | [`.agents/skills/`](.agents/skills/), `skills-lock.json` |
| Configured Superpowers | Upstream plugin with strict workflows made explicit-only | [`config/superpowers.json`](config/superpowers.json)  |
| Plugin setup           | Desired Codex and Claude plugin sets                     | [`config/`](config/)                                  |
| Machine setup          | Bootstrap, refresh, configuration, and verification      | [`scripts/`](scripts/)                                |

The top-level [`skills/`](skills/) directory intentionally contains only the three workflows maintained here. The
five third-party skills are installed at project scope by the official `skills` CLI, committed under
[`.agents/skills/`](.agents/skills/), and tracked by `skills-lock.json`. Do not edit those upstream snapshots by
hand; use `npm run skills:update` and review the resulting diff.

## Catalog

Browse the canonical setup in a searchable local web catalog:

```bash
npm run catalog
```

Open [localhost:4173/catalog/](http://127.0.0.1:4173/catalog/). To compare the repository with installed plugins and
skills on the current Mac, run `npm run catalog:snapshot`, reopen the catalog with `?runtime=local`, and choose
**This Mac**. The snapshot is private, machine-local, and ignored by Git.

## Common commands

| Command                               | Purpose                                            |
| ------------------------------------- | -------------------------------------------------- |
| `./scripts/bootstrap.sh`              | Reapply shared links and non-secret runtime policy |
| `./scripts/refresh-codex-plugins.sh`  | Refresh the desired Codex plugin set               |
| `./scripts/refresh-claude-plugins.sh` | Refresh the desired Claude plugin set              |
| `./scripts/verify-setup.sh`           | Compare this Mac with the desired setup            |
| `npm run skills:update`               | Check and apply upstream skill updates for review   |
| `npm run superpowers:check`           | Check whether the fork trails upstream             |
| `npm run catalog`                     | Generate and serve the browser catalog             |
| `npm run verify`                      | Run the complete local and GitHub Actions gate     |

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
- [Maintenance](inventory/maintenance.md): updates, plugin refreshes, Superpowers review, and releases.
- [Authoring checks](inventory/authoring.md): linting, formatting, validation, and behavioral testing for skills and plugins.
- [Outstanding work](inventory/next-steps.md): the remaining authentication-dependent and MacBook setup tasks.
- [Migration record](inventory/publication.md): completed cross-repository rollout.
- [Repository inventory](inventory/repos.md): repositories governed by the shared setup.
- [Changelog](CHANGELOG.md): curated repository releases and upgrade notes.

## Releases

Repository releases use `vMAJOR.MINOR.PATCH` tags and curated notes from `CHANGELOG.md`. The configured Superpowers
fork has its own upstream-derived version and release process. See the
[maintenance guide](inventory/maintenance.md#release-agent-tooling) for both update paths.
