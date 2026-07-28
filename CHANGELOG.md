# Changelog

All notable changes to the shared agent-tooling setup are documented here. The repository follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); individual plugins may keep an independent manifest
version when compatibility requires it.

## [Unreleased]

### Added

- A generated browser catalog for searching and filtering canonical skills and plugins.
- Optional machine-local inventory snapshots that distinguish installed runtime state from Git-backed desired state.
- Catalog drift verification in the local and GitHub Actions repository gate.

### Changed

- Reworked the README into a concise repository landing page with standard navigation and commands.
- Standardized future repository releases on `vMAJOR.MINOR.PATCH` tags with curated changelog notes.

## [0.2.0] - 2026-07-27

### Added

- One canonical `AGENTS.md` working agreement shared by Codex and Claude Code.
- Portable personal skills for SwiftUI, Apple-style design, motion review, and code-native UI ideation.
- Patrick Delivery workflows for proportional feature delivery and explicit specification, planning, strict TDD,
  execution, and production hardening.
- Desired plugin manifests, new-machine setup scripts, and cross-machine setup verification.
- Firebase and Firestore safety boundaries for emulators, privileged Admin SDK access, rules, indexes, and live data.
- CI, pinned linting and formatting, Dependabot, Gitleaks, and protected-branch verification.

### Changed

- Replaced implicit Superpowers workflows with selective personal workflows so lightweight UI iteration remains light.
- Made generated-image UI ideation opt-in and code-native browser or simulator exploration the default.
- Made `AGENTS.md` canonical while retaining Claude compatibility links and repository shims where useful.

### Security

- Added staged, pre-push, and full-history Gitleaks checks as the private-repository secret-scanning fallback.
- Kept credentials, OAuth sessions, production data, and machine-specific trust state outside the Git-backed setup.

### Upgrade notes

Pull the repository, run `./scripts/bootstrap.sh`, refresh the configured Codex and Claude plugins, and start new
tasks in both products.

[unreleased]: https://github.com/pdugan20/agent-tooling/compare/patrick-delivery-v0.2.0...HEAD
[0.2.0]: https://github.com/pdugan20/agent-tooling/releases/tag/patrick-delivery-v0.2.0
