# Repository migration inventory

Audit date: 2026-07-26

This inventory covers top-level Git worktrees in `/Users/patrickdugan/Documents/Github` plus the active Messenger repository at `/Users/patrickdugan/Documents/messenger`.

## Migration rule

Migrate each remote once from its canonical checkout. Do not edit suffixed linked worktrees independently; they inherit repository instructions when the canonical migration lands on the default branch.

## Published and local migration state

All canonical repositories have been handled. The 23 remote-backed repositories have a published `codex/agent-workflow-migration` branch whose remote SHA was verified against the reviewed local commit on 2026-07-26. The five current-priority repositories have draft pull requests; later waves are pushed but intentionally do not have pull requests yet. Local-only repositories use the same branch name based on local `main`.

| Repository                 | Commit     | Publication status                                                  | Notes                                                                  |
| -------------------------- | ---------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `agent-tooling`            | `main`     | Private remote: `pdugan20/agent-tooling`                            | Shared source, installer, inventory, and Patrick Delivery plugin       |
| `nextup-ios-app`           | `a2eae9f8` | [Draft PR #772](https://github.com/nxt-up/nextup-ios-app/pull/772)  | Canonical skills plus Claude symlinks                                  |
| `nextup-backend`           | `319117e5` | [Draft PR #740](https://github.com/nxt-up/nextup-backend/pull/740)  | Canonical skills, explicit-only TDD, MCP docs, and legacy-link shim    |
| `nextup-web`               | `fef3229`  | [Draft PR #117](https://github.com/nxt-up/nextup-web/pull/117)      | Exploration/production modes and Firebase safety                       |
| `pat-portfolio`            | `fc14e65`  | [Draft PR #87](https://github.com/pdugan20/pat-portfolio/pull/87)   | Existing guidance preserved in canonical `AGENTS.md`                   |
| `messenger`                | `02d8f21`  | [Draft PR #15](https://github.com/pdugan20/messenger-proto/pull/15) | Expo design-iteration mode and explicit strict TDD                     |
| `chat-app-prototype`       | `6cb668e`  | Branch pushed; Wave 3 PR pending                                    | React Native / Expo guidance                                           |
| `claude-usage`             | `f60bb43`  | Branch pushed; Wave 3 PR pending                                    | Swift guidance; Claude references retained where they describe product |
| `claudelint`               | `3b48ca4`  | Branch pushed; Wave 2 PR pending                                    | Root/nested guides plus one canonical shared skill                     |
| `claudenotes`              | `5c5d6d4`  | Branch pushed; Wave 3 PR pending                                    | Next.js guidance                                                       |
| `e-ink-scoreboard`         | `825d544`  | Branch pushed; Wave 3 PR pending                                    | Python/JavaScript guidance                                             |
| `figma-chat-builder`       | `82a0a6f`  | Branch pushed; Wave 3 PR pending                                    | Figma TypeScript guidance; strict hooks and 88 tests passed            |
| `figma-music-injector`     | `e08ddca`  | Branch pushed; Wave 3 PR pending                                    | Figma TypeScript guidance                                              |
| `imessage-swift-prototype` | `936dcd7`  | Branch pushed; Wave 3 PR pending                                    | SwiftUI exploration guidance                                           |
| `libby-downloader`         | `51f0088`  | Branch pushed; Wave 3 PR pending                                    | TypeScript CLI guidance                                                |
| `mintlify-docs`            | `9eb14ed`  | Branch pushed; Wave 2 PR pending                                    | Cross-runtime contributor guide without shipping plugin context        |
| `passant-prototype`        | `223d62c`  | Branch pushed; Wave 3 PR pending                                    | React Native / Expo guidance                                           |
| `rss-feed-generator`       | `671127a`  | Branch pushed; Wave 3 PR pending                                    | TypeScript service guidance                                            |
| `touchpoint`               | `6376a64`  | Branch pushed; Wave 3 PR pending                                    | macOS prototype guidance                                               |
| `x-archive`                | `0c2696c`  | Branch pushed; Wave 3 PR pending                                    | Next.js/Supabase guidance                                              |
| `bibliocommons-mcp`        | `7a9583f`  | Branch pushed; Wave 2 PR pending                                    | Live library-account mutation boundary                                 |
| `clickwheel`               | `9c27552`  | Branch pushed; Wave 2 PR pending                                    | Client-independent MCP safety plus canonical docs-mirror guidance      |
| `presentations`            | `6f5f2b9`  | Branch pushed; Wave 2 PR pending                                    | Lightweight narrative/visual iteration mode                            |
| `rewind`                   | `0fa60c9`  | Branch pushed; Wave 2 PR pending                                    | Three canonical shared skills plus live API/data boundaries            |
| `github-automation`        | `5e0f4b5`  | Local only; remote decision pending                                 | Preserves the read-only control-plane invariant                        |
| `github-portfolio-ops`     | `6f38a51`  | Local only; remote decision pending                                 | Historical Superpowers artifacts do not trigger workflow               |

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

## Remaining publication decisions

- Review and merge the five Wave 1 draft pull requests; no migration pull request is configured to merge automatically.
- Open Wave 2 and Wave 3 pull requests when the first wave has been reviewed and notification volume is acceptable.
- Decide whether `github-automation` and `github-portfolio-ops` should remain local-only, be archived, or receive private remotes before attempting to sync them.
- Do not push a direct migration to `clickwheel-fm-docs`; let its existing source-mirror workflow carry the nested docs guidance after `clickwheel` is merged.

## Local environment status and follow-ups

- Codex CLI `0.145.0` is installed and passes a fresh-process exploration-mode smoke test. The stale `supports_reasoning_summaries` model-cache warning and skill-description budget warning no longer appear.
- The Computer Use MCP command now uses its verified absolute executable path. `codex doctor` reports the MCP configuration locally consistent; `scripts/configure-codex.py` applies the same non-secret repair idempotently on other machines when that executable exists.
- The NextUp backend MCP endpoint is configured and advertises OAuth correctly, but authentication is intentionally deferred because the 2026-07-26 browser flow did not complete. No credentials were stored; `codex mcp list` reports `Not logged in`. Retry later with `codex mcp login nextup-mcp-dev`, approve `library:read` and `ugc:write` in the browser, then confirm the listing shows OAuth.
- A fresh Codex `0.145.0` process logs non-blocking validation warnings from bundled OpenAI plugins: the spreadsheet skill's icons escape its asset directory, and template-creator supplies more than three default prompts. These are upstream cache contents, not personal-plugin defects; do not patch generated plugin caches.
- The fresh process also logged transient rollout lookup fallbacks, while `codex doctor` independently reported healthy databases and exact rollout/state-DB parity. Reinvestigate only if thread listing or resume behavior becomes visibly incorrect.
- A no-tool Claude startup loaded about 34.5k context tokens and passed the routing smoke test. Keep configuration smoke tests to one turn; repeated tool turns rewrite/cache that context and cost substantially more.
- Installing `clickwheel/tools/ci` from its lockfile for the repository hook reported 16 existing high-severity npm audit findings. The migration changed no dependencies; investigate separately and do not run `npm audit fix --force` as part of this workflow migration.
