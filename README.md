# Agent Tooling

[![CI](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml/badge.svg)](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml)
![Codex](https://img.shields.io/badge/Codex-configured-111111?logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-configured-D97757)
![Node](https://img.shields.io/badge/Node-22-3C873A?logo=nodedotjs&logoColor=white)

Private, canonical tooling shared across Patrick's Codex and Claude Code projects: working agreements, personal
skills, a policy-configured Superpowers fork, plugin manifests, and machine setup.

## Quick start

Install and authenticate Codex, Claude Code, and GitHub CLI, then run:

```bash
gh repo clone pdugan20/agent-tooling ~/Documents/Github/agent-tooling
cd ~/Documents/Github/agent-tooling
./scripts/setup-new-machine.sh
```

Restart Codex and Claude afterward. Product OAuth sessions, API keys, local toolchains, and repository-specific
instructions remain machine- or project-local.

## Included

| Area                   | Purpose                                                        | Canonical source                               |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------- |
| Shared instructions    | Exploration, production, Firebase, and safety policy           | [`global/AGENTS.md`](global/AGENTS.md)         |
| Personal skills        | Design, SwiftUI, motion, feature delivery, and hardening       | [`skills/`](skills/)                           |
| Configured Superpowers | Upstream plugin with strict workflows made explicit-only       | [`config/superpowers.json`](config/superpowers.json) |
| Plugin setup           | Desired Codex and Claude plugin sets                           | [`config/`](config/)                           |
| Machine setup          | Bootstrap, refresh, configuration, and verification            | [`scripts/`](scripts/)                         |

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
- [Migration record](inventory/publication.md): completed cross-repository rollout.
- [Repository inventory](inventory/repos.md): repositories governed by the shared setup.
- [Changelog](CHANGELOG.md): curated repository releases and upgrade notes.

## Releases

Repository releases use `vMAJOR.MINOR.PATCH` tags and curated notes from `CHANGELOG.md`. The configured Superpowers
fork has its own upstream-derived version and release process. See the
[maintenance guide](inventory/maintenance.md#release-agent-tooling) for both update paths.
