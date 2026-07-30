# Changelog

All notable changes to the shared agent-tooling setup are documented here. The repository follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); individual plugins may keep an independent manifest
version when compatibility requires it.

## [Unreleased]

## [0.4.1] - 2026-07-30

### Fixed

- Retire the legacy personal plugin and marketplace before registering or updating `patrick-tools`, preventing the
  redirected repository from failing Codex marketplace upgrades with an identity mismatch.

## [0.4.0] - 2026-07-30

### Added

- Added an MIT license and standardized repository badges for CI, releases, Node.js support, and licensing.
- Added `npm run mcp:check` as a repeatable machine-local MCP authentication status check.
- Added canonical GitHub source links to catalog skill and plugin records wherever a public source exists.
- Documented that Claude's LSP plugins are runtime-specific, installed the TypeScript language-server prerequisite
  during new-machine setup, and added binary checks to setup verification.
- Added Emil Kowalski's upstream-managed `find-animation-opportunities` and `pick-ui-library` skills for both
  Codex and Claude Code.
- Documented the audited global-versus-project scope model, including the narrow project-pinned Apple reference
  profile.
- Added Typos spelling checks, zizmor workflow-security analysis, and scheduled Lychee link validation with pinned
  releases and documented adoption criteria.

### Changed

- Made the repository public, removed obsolete visibility language, and standardized documented operator commands on
  stable `npm run` entry points.
- Consolidated current documentation around architecture, maintenance, and authoring; removed completed migration
  ledgers and machine-specific task tracking from the maintained documentation set.
- Split Codex account-managed plugins from marketplace-installed plugins so setup no longer installs duplicate CLI
  copies of Figma, GitHub, or Vercel, and made the Plugins tab the documented authority for that managed layer.
- Audited every desired Codex plugin against its vendor source. Expo, Sentry, and Mintlify now use current
  vendor-backed Git marketplace packages; their superseded curated or pinned installs are removed during setup.
- Kept Figma, GitHub, and Vercel on Codex-curated packages where Codex-specific tool-schema adaptation or connected
  app capabilities outweigh the newer direct package.
- Added the current official Expo plugin to Claude's desired state so both runtimes use the same Expo source.
- Distinguished canonical management scope from effective runtime availability in the catalog and documentation;
  shared capabilities are now labeled “All repositories.”
- Documented the official skills CLI's current update and cross-agent frontmatter limitations so upstream snapshots
  remain updateable without hidden local forks.
- Removed Claude's always-on `explanatory-output-style` plugin from desired state because its SessionStart hook adds
  mandatory educational output and token overhead to every task.
- Added portable project-skill discovery to the local catalog snapshot with repository and availability filters;
  repository roots are supplied at runtime and never committed.
- Grouped equivalent Codex and Claude plugin packages into one catalog capability with per-runtime installation
  details, and made Claude setup honor the active `CLAUDE_CONFIG_DIR` profile.
- Reconciled Claude's enabled user-scoped plugins to the canonical manifest during setup and refresh by disabling,
  rather than uninstalling, undeclared plugins.
- Moved the three Patrick-owned workflows to the public, versioned `pdugan20/patrick-workflows` collection and now
  consume its v1.0.0 release through Skills CLI-managed snapshots and provenance hashes.
- Renamed the personal marketplace to `patrick-tools`, migrated both runtime plugin IDs, and now remove the retired
  marketplace registration during setup and refresh.
- Updated Mintlify Docs to v0.3.2 so both runtimes layer on Mintlify's current vendor-maintained plugin source.

### Security

- Added medium-or-higher GitHub Actions security enforcement and narrowed release and scheduled-workflow
  permissions based on the zizmor audit.

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

- Added staged, pre-push, and full-history Gitleaks checks as complementary secret-scanning layers.
- Kept credentials, OAuth sessions, production data, and machine-specific trust state outside the Git-backed setup.

### Upgrade notes

Pull the repository, run `npm run bootstrap`, refresh the configured Codex and Claude plugins, and start new
tasks in both products.

[unreleased]: https://github.com/pdugan20/agent-tooling/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/pdugan20/agent-tooling/compare/patrick-delivery-v0.2.0...v0.3.0
[0.2.0]: https://github.com/pdugan20/agent-tooling/releases/tag/patrick-delivery-v0.2.0
