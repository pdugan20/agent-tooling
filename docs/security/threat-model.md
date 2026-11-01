# Security threat model

## Scope and protected assets

This public repository configures Codex and optional Claude Code through linked instructions, skills, plugins, and settings. A local catalog displays selections and machine observations; tagged workflows publish GitHub releases (`README.md`, `scripts/bootstrap.sh`, `.github/workflows/release.yml`).

Protect instruction/executable integrity, user configuration and work, connector credentials, private inventory, and release authority. Accounts and credentials persist separately from this checkout (`global/AGENTS.md`, `docs/architecture.md`).

## Entry points

- Contributors supply instructions, skills, locks, manifests, dependencies, workflows, and release notes (`global/AGENTS.md`, `.agents/skills/`, `skills-lock.json`, `config/`, `package.json`, `.github/workflows/`, `CHANGELOG.md`).
- Local owners and agents supply arguments, environment overrides, paths, settings, hook JSON, and skill metadata. Apps and CLIs supply installation/authentication inventory (`scripts/configure-codex.py`, `scripts/configure-claude.py`, `scripts/generate_catalog.py`, `scripts/check_mcp_auth.py`, `global/hooks/`).
- Repositories, marketplaces, registries, and release hosts supply code and instructions; GitHub supplies events and pull-request metadata (`scripts/install-codex-plugins.sh`, `scripts/install-ci-tools.sh`, `global/hooks/agent_push_scope.py`).
- Browsers request catalog assets and remote images. Skill helpers accept media, browser URLs, and output paths (`catalog/src/catalog.ts`, `catalog/src/components/source-identity.tsx`, `.agents/skills/analyze-ui-video/scripts/video_frames.py`, `.agents/skills/stageshow/scripts/film.mjs`).

## Trust boundaries and assumptions

Setup uses the invoking account's filesystem and CLI privileges. Checkout updates can change globally linked agent behavior. Preserve unrelated settings and conflicting local paths (`scripts/bootstrap.sh`, `scripts/configure-codex.py`, `scripts/configure-claude.py`).

Instructions, tool output, and hook input cross into agent context or subprocess arguments. They must not grant publication, deployment, destructive-action, or live-data authority. Harness permissions and service authorization must enforce user scope; metadata and hooks must not replace these boundaries (`global/AGENTS.md`, `docs/skill-invocation.md`, `global/hooks/`).

## Sensitive data and privileged actions

Settings writers install hook commands. MCP configuration selects local processes, debugging/UI workflows, and a CircleCI tool allowlist. Authentication checks report CLI status; connector login remains separate (`config/codex-mcp-servers.json`, `scripts/check_mcp_auth.py`, `docs/setup.md`).

Local snapshots contain paths, descriptions, and installation state. Exclude credentials and configuration values. Release and scheduled-issue jobs use distinct GitHub write permissions (`scripts/generate_catalog.py`, `.gitignore`, `.github/workflows/release.yml`, `.github/workflows/superpowers-update-check.yml`).

## Principal threats and required controls

- Supply-chain compromise: review source identity, refs, content diffs, hashes, and exceptions together. Validate resource/symlink containment; retain action pins, archive checksums, and reviewed updates (`docs/maintenance.md`, `scripts/check_skill_snapshots.mjs`, `scripts/check_skill_ownership.py`, `scripts/install-ci-tools.sh`, `renovate.json`).
- Authority expansion: retain explicit invocation/action approval, MCP restrictions, and hook trust review. Separate arguments from shell syntax and preserve unrelated hooks/settings (`global/AGENTS.md`, `config/codex-mcp-servers.json`, `scripts/configure-codex.py`, `scripts/configure-claude.py`).
- Disclosure or unintended writes: keep previews local, constrain served files and resolved paths, validate output destinations, and render metadata as text. Exclude private snapshots from distribution and retain secret scanning (`catalog/vite.config.ts`, `scripts/serve_catalog.py`, `scripts/generate_catalog.py`, `catalog/src/components/catalog-detail.tsx`, `.gitignore`, `scripts/verify-repo.sh`).
- CI/release tampering: retain read-only pull-request CI, unpersisted checkout credentials, scoped write tokens, and tag/version/changelog verification before publishing (`.github/workflows/ci.yml`, `.github/workflows/release.yml`, `scripts/validate_repository.py`).

## Review priorities

Review instructions, configuration writers, hooks, MCP privileges, and installed sources first; then CI/release authority and catalog data handling. Check configuration preservation, link conflicts, malformed input, and provenance drift (`docs/authoring.md`, `scripts/test_setup.py`, `scripts/test_skill_snapshots.py`).

## Uncertain assumptions

- Effective harness permissions, hook trust, connector grants, and installed CLI behavior are unconfirmed (`docs/architecture.md`, `docs/setup.md`).
- GitHub branch/tag protections, required checks, and installed automation permissions are unconfirmed (`.github/workflows/`, `renovate.json`).
- Current remote package contents and third-party service enforcement are unconfirmed (`skills-lock.json`, `config/codex-mcp-auth.json`, `config/codex-plugins.txt`).

## When to update this model

Update when trust, sources, configuration ownership, hooks, MCP privileges, credentials, preview exposure, or release authority changes. Recheck assumptions after runtime or hosting-policy changes (`docs/architecture.md`, `docs/maintenance.md`).
