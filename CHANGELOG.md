# Changelog

All notable changes to the shared agent-tooling setup are documented here. The repository follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); individual plugins may keep an independent manifest
version when compatibility requires it.

## [Unreleased]

### Added

- Added Emil Kowalski's upstream-managed `find-animation-opportunities` and `pick-ui-library` skills for both
  Codex and Claude Code.
- Documented the audited global-versus-project scope model, including the narrow project-pinned Apple reference
  profile.

### Changed

- Distinguished canonical management scope from effective runtime availability in the catalog and documentation;
  shared capabilities are now labeled “All repositories.”
- Documented the official skills CLI's current update and cross-agent frontmatter limitations so upstream snapshots
  remain updateable without hidden local forks.
- Removed Claude's always-on `explanatory-output-style` plugin from desired state because its SessionStart hook adds
  mandatory educational output and token overhead to every task.
- Added portable project-skill discovery to the private catalog snapshot with repository and availability filters;
  repository roots are supplied at runtime and never committed.

## [0.3.0] - 2026-07-28

### Added

- A generated browser catalog for searching and filtering canonical skills and plugins.
- Optional machine-local inventory snapshots that distinguish installed runtime state from Git-backed desired state.
- Catalog drift verification in the local and GitHub Actions repository gate.
- A thin, upstream-tracking Superpowers fork with policy tests and a weekly upstream-change monitor.
- Official `skills` CLI lockfile management for the four Emil Kowalski skills and Paul Hudson's `swiftui-pro`.
- Dual-runtime desired state for the shared `mintlify-docs` plugin.

### Changed

- Reworked the README into a concise repository landing page with standard navigation and commands.
- Standardized future repository releases on `vMAJOR.MINOR.PATCH` tags with curated changelog notes.
- Replaced the duplicated Patrick Delivery wrapper with the configured Superpowers plugin plus two clearly owned
  personal skills: `feature-delivery` and `production-hardening`.
- Made Superpowers planning, brainstorming, TDD, worktree, parallel-agent, and branch-finishing workflows
  explicit-only while keeping debugging, review, verification, and skill-authoring workflows available automatically.
- Removed Superpowers' automatic session router and browser-based visual option picker.
- Exercised the upstream-update path against a documentation-only Superpowers change and advanced the configured
  fork baseline to `6.2.0-config.2`.
- Made new-machine setup and migration auditing independent of a username or fixed checkout directory.
- Reduced `skills/` to the three workflows maintained in this repository; third-party snapshots now live under
  `.agents/skills/` with their original source and creator shown in the catalog.
- Added source-lock and compatibility-link validation so copied or silently diverged upstream skills fail CI.

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

[unreleased]: https://github.com/pdugan20/agent-tooling/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/pdugan20/agent-tooling/compare/patrick-delivery-v0.2.0...v0.3.0
[0.2.0]: https://github.com/pdugan20/agent-tooling/releases/tag/patrick-delivery-v0.2.0
