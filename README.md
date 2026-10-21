# agent-tooling

[![CI](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/pdugan20/agent-tooling/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/pdugan20/agent-tooling)](https://github.com/pdugan20/agent-tooling/releases/latest)
[![License](https://img.shields.io/github/license/pdugan20/agent-tooling)](LICENSE)

Patrick's reproducible agent setup: shared instructions, pinned skills, plugin selections, and machine configuration.
Codex is the primary harness; Claude Code is an optional companion.

## Setup

Follow the [setup guide](docs/setup.md) for prerequisites, installation, and checks.
`npm run setup` configures Codex; `npm run setup:claude` adds the optional Claude Code setup.

Reusable Patrick-owned skills are authored in [Skills](https://github.com/pdugan20/skills).
This repository selects their releases alongside third-party skills and links the locked snapshots into the runtimes.
See the [architecture](docs/architecture.md) for ownership and scope.

## Browse the setup

```bash
npm ci
npm run catalog
```

The catalog shows the selected capabilities and their sources. Its optional **This Mac** snapshot compares installed
state within the scanner's coverage; it is not a complete machine inventory. See [catalog usage](docs/setup.md#browse-the-catalog).

## Development

```bash
nvm use
npm ci
npm run verify
```

Install the [verification prerequisites](docs/setup.md#develop-this-repository) before the first run.

- [Maintenance](docs/maintenance.md): update skills, plugins, the catalog, and releases.
- [Skill invocation](docs/skill-invocation.md): Codex controls and Claude compatibility.
- [Authoring](docs/authoring.md): validation and runtime checks.
- [Quality tooling](docs/quality-tooling.md): repository gates and dependency policy.
- [Writing style](docs/output-styles.md): Codex instructions and the Claude-only output style.
- [Documentation audit](docs/documentation-audit.md): verified guidance and remaining follow-ups.
- [Changelog](CHANGELOG.md): releases and upgrade notes.
