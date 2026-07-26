# Repository migration inventory

Audit date: 2026-07-26

This inventory covers top-level Git worktrees in `/Users/patrickdugan/Documents/Github` plus the active Messenger repository at `/Users/patrickdugan/Documents/messenger`.

## Migration rule

Migrate each remote once from its canonical checkout. Do not edit suffixed linked worktrees independently; they inherit repository instructions when the canonical migration lands on the default branch.

## Completed locally, not pushed

| Repository       | Local branch                     | Commit     | Notes                                                      |
| ---------------- | -------------------------------- | ---------- | ---------------------------------------------------------- |
| `agent-tooling`  | `main`                           | `caa2fee`  | New local private-tooling source; no remote yet            |
| `nextup-ios-app` | `codex/agent-workflow-migration` | `a2eae9f8` | Canonical skills plus Claude symlinks                      |
| `nextup-backend` | `codex/agent-workflow-migration` | `72eea95b` | Canonical skills; TDD/live-test workflows explicit-only    |
| `nextup-web`     | `codex/agent-workflow-migration` | `fef3229`  | Exploration/production modes and Firebase safety           |
| `pat-portfolio`  | `codex/agent-workflow-migration` | `fc14e65`  | Current `main` guidance preserved in canonical `AGENTS.md` |
| `messenger`      | `codex/agent-workflow-migration` | `02d8f21`  | Expo design-iteration mode and explicit strict TDD         |

## Remaining canonical repositories

### Existing `AGENTS.md`; consolidate duplicate guidance

| Repository          | State                                                            | Recommended action                                                          |
| ------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `bibliocommons-mcp` | Dirty primary worktree; `AGENTS.md` and `CLAUDE.md` both present | Preserve WIP, make `AGENTS.md` canonical, reduce Claude file to import/shim |
| `clickwheel`        | Dirty primary worktree; two Superpowers references               | Preserve WIP, audit the strict-workflow language, then consolidate          |
| `presentations`     | Dirty primary worktree                                           | Preserve ten local changes; consolidate through an isolated branch          |

### Claude-only repository skills

| Repository   | Skills | Recommended action                                                                                              |
| ------------ | -----: | --------------------------------------------------------------------------------------------------------------- |
| `claudelint` |      1 | Move canonical source to `.agents/skills`, add per-skill Claude symlink, validate                               |
| `rewind`     |      3 | Preserve four local changes, move canonical source to `.agents/skills`, add per-skill Claude symlinks, validate |

### `CLAUDE.md` only; add canonical `AGENTS.md`

| Repository                 | Default branch | Notes                                               |
| -------------------------- | -------------- | --------------------------------------------------- |
| `chat-app-prototype`       | `main`         | React Native / Expo                                 |
| `claude-usage`             | `main`         | Claude tooling                                      |
| `claudelint`               | `main`         | Also needs skill conversion                         |
| `claudenotes`              | `main`         | TypeScript app                                      |
| `e-ink-scoreboard`         | `main`         | TypeScript and Python                               |
| `figma-chat-builder`       | `main`         | Figma-oriented TypeScript                           |
| `figma-music-injector`     | `main`         | Figma-oriented TypeScript                           |
| `imessage-swift-prototype` | `main`         | Swift prototype                                     |
| `libby-downloader`         | `main`         | TypeScript                                          |
| `passant-prototype`        | `master`       | React Native / Expo                                 |
| `rewind`                   | `main`         | Dirty primary worktree; also needs skill conversion |
| `rss-feed-generator`       | `main`         | TypeScript                                          |
| `touchpoint`               | `master`       | Prototype                                           |
| `x-archive`                | `main`         | TypeScript                                          |

### No repository instruction file

| Repository             | State                                                | Recommended action                                             |
| ---------------------- | ---------------------------------------------------- | -------------------------------------------------------------- |
| `clickwheel-fm-docs`   | External organization remote; current feature branch | Confirm ownership/scope before adding instructions             |
| `github-automation`    | Local-only repository                                | Decide whether to keep local, archive, or add a private remote |
| `github-portfolio-ops` | Local-only repository                                | Decide whether to keep local, archive, or add a private remote |
| `mintlify-docs`        | Clean `main`                                         | Add a concise docs-specific `AGENTS.md` if active              |

## Existing linked worktrees and duplicate checkouts

Do not migrate these separately:

- `bibliocommons-mcp-vite6-bridge`
- `chat-app-cooldown-hardening`
- `chat-app-prototype-automation-hardening`
- `chat-app-prototype-pr68-repair`
- `claudelint-upload-artifact-v7`
- `claudenotes-automation-hardening`
- `claudenotes-rls-ci`
- `claudenotes-svix-direct`
- `imessage-swift-prototype-automation-hardening`
- `nextup-backend-deploy-packaging`
- `nextup-ios-app-appclip-guest`
- `nextup-ios-app-sentry-remediation`
- `nextup-ios-app-slack-events`
- `nextup-ios-app-swiftpm-ci-hardening`
- `nextup-web-automation-hardening`
- `nextup-web-js-yaml-4-2-0`
- `nextup-web-sentry-remediation`
- `pat-portfolio-poster-hotfix`
- `pat-portfolio-poster-sizing`
- `pat-portfolio-recent-listening`
- `pat-portfolio-watching`
- `rewind-automation-hardening`
- `rewind-docs-almond`
- `rewind-listening-tracks`
- `rewind-pr119-refresh`
- `rewind-recent-listening`
- `rewind-toolchain-security-bridge`
- `rewind-watching-images`
- `rewind-workers-test-toolchain`
- `touchpoint-automation-hardening`
- `x-archive-automation-hardening`
- `x-archive-security-bridge`

## Remote actions awaiting explicit approval

- Create a private GitHub remote for `agent-tooling` and push `main`.
- Push the five `codex/agent-workflow-migration` branches and open reviewable pull requests.
- Batch the remaining clean repositories first; isolate dirty repositories through clean worktrees based on their remote default branches.

## Local environment follow-ups

- Codex CLI `0.145.0` is available; this machine currently runs `0.144.1`. Re-run the fresh-process smoke test after updating, especially the stale model-cache warning about `supports_reasoning_summaries`.
- The NextUp backend MCP endpoint requires authentication and logs an auth warning in a fresh Codex session. Authenticate it or disable that repository MCP server when it is not in use.
- `codex doctor` reports the terminal-hosted Computer Use command as unresolved because its configured command is relative. The desktop plugin works; recheck this after the Codex update before changing configuration.
- Codex shortened skill descriptions to fit its 2% skill-context budget. If automatic routing becomes unreliable, disable plugins that are not relevant to the current stack or use a leaner profile.
- A no-tool Claude startup loaded about 34.5k context tokens and passed the routing smoke test. Keep configuration smoke tests to one turn; repeated tool turns rewrite/cache that context and cost substantially more.
