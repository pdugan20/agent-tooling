# Repository migration inventory

Audit date: 2026-07-26

This inventory covers top-level Git worktrees in `/Users/patrickdugan/Documents/Github` plus the active Messenger repository at `/Users/patrickdugan/Documents/messenger`.

## Migration rule

Migrate each remote once from its canonical checkout. Do not edit suffixed linked worktrees independently; they inherit repository instructions when the canonical migration lands on the default branch.

## Completed locally, not pushed

All canonical repositories have been handled. Remote-backed repositories use a local `codex/agent-workflow-migration` branch based on the current remote default branch. Local-only repositories use the same branch name based on local `main`.

| Repository                 | Commit     | Notes                                                                  |
| -------------------------- | ---------- | ---------------------------------------------------------------------- |
| `agent-tooling`            | local main | Private-tooling source; no remote yet                                  |
| `nextup-ios-app`           | `a2eae9f8` | Canonical skills plus Claude symlinks                                  |
| `nextup-backend`           | `72eea95b` | Canonical skills; TDD/live-test workflows explicit-only                |
| `nextup-web`               | `fef3229`  | Exploration/production modes and Firebase safety                       |
| `pat-portfolio`            | `fc14e65`  | Existing guidance preserved in canonical `AGENTS.md`                   |
| `messenger`                | `02d8f21`  | Expo design-iteration mode and explicit strict TDD                     |
| `chat-app-prototype`       | `6cb668e`  | React Native / Expo guidance                                           |
| `claude-usage`             | `f60bb43`  | Swift guidance; Claude references retained where they describe product |
| `claudelint`               | `3b48ca4`  | Root/nested guides plus one canonical shared skill                     |
| `claudenotes`              | `5c5d6d4`  | Next.js guidance                                                       |
| `e-ink-scoreboard`         | `825d544`  | Python/JavaScript guidance                                             |
| `figma-chat-builder`       | `82a0a6f`  | Figma TypeScript guidance; strict hooks and 88 tests passed            |
| `figma-music-injector`     | `e08ddca`  | Figma TypeScript guidance                                              |
| `imessage-swift-prototype` | `936dcd7`  | SwiftUI exploration guidance                                           |
| `libby-downloader`         | `51f0088`  | TypeScript CLI guidance                                                |
| `mintlify-docs`            | `9eb14ed`  | Cross-runtime contributor guide without shipping plugin context        |
| `passant-prototype`        | `223d62c`  | React Native / Expo guidance                                           |
| `rss-feed-generator`       | `671127a`  | TypeScript service guidance                                            |
| `touchpoint`               | `6376a64`  | macOS prototype guidance                                               |
| `x-archive`                | `0c2696c`  | Next.js/Supabase guidance                                              |
| `bibliocommons-mcp`        | `7a9583f`  | Live library-account mutation boundary                                 |
| `clickwheel`               | `9c27552`  | Client-independent MCP safety plus canonical docs-mirror guidance      |
| `presentations`            | `6f5f2b9`  | Lightweight narrative/visual iteration mode                            |
| `rewind`                   | `0fa60c9`  | Three canonical shared skills plus live API/data boundaries            |
| `github-automation`        | `5e0f4b5`  | Local-only; preserves the read-only control-plane invariant            |
| `github-portfolio-ops`     | `6f38a51`  | Local-only; historical Superpowers artifacts do not trigger workflow   |

## Generated mirror exception

`clickwheel-fm-docs` is an external-organization, one-way generated mirror of `clickwheel/docs-mintlify`. It must not be edited directly. The `clickwheel` migration adds `docs-mintlify/AGENTS.md` and its Claude shim at commit `9c27552`; the existing mirror workflow will copy them only after that source branch is merged and synced.

## Preserved primary-worktree state

The migration used isolated worktrees, so existing primary-checkout work remains unchanged. In particular:

- `bibliocommons-mcp`, `clickwheel`, and `presentations` retain their untracked local `AGENTS.md` files and other active changes.
- `rewind` retains its modified `CLAUDE.md`, reading/watching domain edits, historical Superpowers plans, and local feature-branch commit.
- The previously recorded NextUp, portfolio, and Messenger work-in-progress remains untouched.
- `nextup-backend` has two pre-existing `lint-staged automatic backup` recovery stashes, dated 2026-07-26 07:33 and 2026-07-18 21:41. They contain unrelated notification-quality and public-profile reconciliation work and were deliberately preserved.

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
- Push the 23 remote-backed `codex/agent-workflow-migration` branches and open reviewable pull requests.
- Decide whether `github-automation` and `github-portfolio-ops` should remain local-only, be archived, or receive private remotes before attempting to sync them.
- Do not push a direct migration to `clickwheel-fm-docs`; let its existing source-mirror workflow carry the nested docs guidance after `clickwheel` is merged.

## Local environment follow-ups

- Codex CLI `0.145.0` is available; this machine currently runs `0.144.1`. Re-run the fresh-process smoke test after updating, especially the stale model-cache warning about `supports_reasoning_summaries`.
- The NextUp backend MCP endpoint requires authentication and logs an auth warning in a fresh Codex session. Authenticate it or disable that repository MCP server when it is not in use.
- `codex doctor` reports the terminal-hosted Computer Use command as unresolved because its configured command is relative. The desktop plugin works; recheck this after the Codex update before changing configuration.
- Codex shortened skill descriptions to fit its 2% skill-context budget. If automatic routing becomes unreliable, disable plugins that are not relevant to the current stack or use a leaner profile.
- A no-tool Claude startup loaded about 34.5k context tokens and passed the routing smoke test. Keep configuration smoke tests to one turn; repeated tool turns rewrite/cache that context and cost substantially more.
- Installing `clickwheel/tools/ci` from its lockfile for the repository hook reported 16 existing high-severity npm audit findings. The migration changed no dependencies; investigate separately and do not run `npm audit fix --force` as part of this workflow migration.
