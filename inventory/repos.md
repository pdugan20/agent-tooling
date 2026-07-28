# Repository migration inventory

Audit date: 2026-07-26

This inventory records the repository collection used for the completed migration plus Messenger's separate canonical
checkout. The audit script derives the repository collection from the `agent-tooling` checkout by default; override it
with `AGENT_REPOSITORIES_ROOT` and `AGENT_MESSENGER_ROOT` when the checkouts use another layout.

## Migration rule

Migrate each remote once from its canonical checkout. Do not edit suffixed linked worktrees independently; they inherit repository instructions when the canonical migration lands on the default branch.

## Merged and local migration state

All canonical repositories have been handled. The 23 remote-backed migrations passed their applicable checks and
were squash-merged through pull requests on 2026-07-26 and 2026-07-27. GitHub removed every remote
`codex/agent-workflow-migration` branch after merge. Local-only repositories use the same branch name based on local
`main` and remain unpublished by design.

| Repository                 | Commit     | Publication status                                                  | Notes                                                                  |
| -------------------------- | ---------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `agent-tooling`            | `main`     | Private remote: `pdugan20/agent-tooling`                            | Shared source, installer, local workflows, locked upstream skills, and plugin policy |
| `nextup-ios-app`           | `a2eae9f8` | [Merged PR #772](https://github.com/nxt-up/nextup-ios-app/pull/772)  | Canonical skills plus Claude symlinks                                  |
| `nextup-backend`           | `319117e5` | [Merged PR #740](https://github.com/nxt-up/nextup-backend/pull/740)  | Canonical skills, explicit-only TDD, MCP docs, and legacy-link shim    |
| `nextup-web`               | `fef3229`  | [Merged PR #117](https://github.com/nxt-up/nextup-web/pull/117)      | Exploration/production modes and Firebase safety                       |
| `pat-portfolio`            | `fc14e65`  | [Merged PR #87](https://github.com/pdugan20/pat-portfolio/pull/87)   | Existing guidance preserved in canonical `AGENTS.md`                   |
| `messenger`                | `02d8f21`  | [Merged PR #15](https://github.com/pdugan20/messenger-proto/pull/15) | Expo design-iteration mode and explicit strict TDD                     |
| `chat-app-prototype`       | `6cb668e`  | [Merged PR #78](https://github.com/pdugan20/chat-app-prototype/pull/78) | React Native / Expo guidance                                         |
| `claude-usage`             | `f60bb43`  | [Merged PR #7](https://github.com/pdugan20/claude-usage/pull/7)       | Swift guidance; Claude references retained where they describe product |
| `claudelint`               | `79db271`  | [Merged PR #165](https://github.com/pdugan20/claudelint/pull/165)     | Root/nested guides plus one canonical shared skill                    |
| `claudenotes`              | `8e997b7`  | [Merged PR #64](https://github.com/pdugan20/claudenotes/pull/64)      | Next.js guidance replayed over the latest `main`                       |
| `e-ink-scoreboard`         | `825d544`  | [Merged PR #84](https://github.com/pdugan20/e-ink-scoreboard/pull/84) | Python/JavaScript guidance                                            |
| `figma-chat-builder`       | `82a0a6f`  | [Merged PR #96](https://github.com/pdugan20/figma-chat-builder/pull/96) | Figma TypeScript guidance; strict hooks and 88 tests passed         |
| `figma-music-injector`     | `e08ddca`  | [Merged PR #38](https://github.com/pdugan20/figma-music-injector/pull/38) | Figma TypeScript guidance                                         |
| `imessage-swift-prototype` | `936dcd7`  | [Merged PR #5](https://github.com/pdugan20/imessage-swift-prototype/pull/5) | SwiftUI exploration guidance                                    |
| `libby-downloader`         | `51f0088`  | [Merged PR #123](https://github.com/pdugan20/libby-downloader/pull/123) | TypeScript CLI guidance                                             |
| `mintlify-docs`            | `90cab61`  | [Merged PR #23](https://github.com/pdugan20/mintlify-docs/pull/23)   | Cross-runtime contributor guide without shipping plugin context        |
| `passant-prototype`        | `223d62c`  | [Merged PR #65](https://github.com/pdugan20/passant-prototype/pull/65) | React Native / Expo guidance                                        |
| `rss-feed-generator`       | `671127a`  | [Merged PR #42](https://github.com/pdugan20/rss-feed-generator/pull/42) | TypeScript service guidance                                        |
| `touchpoint`               | `6376a64`  | [Merged PR #9](https://github.com/pdugan20/touchpoint/pull/9)        | macOS prototype guidance                                               |
| `x-archive`                | `0553ea9`  | [Merged PR #62](https://github.com/pdugan20/x-archive/pull/62)       | Next.js/Supabase guidance                                              |
| `bibliocommons-mcp`        | `7a9583f`  | [Merged PR #60](https://github.com/pdugan20/bibliocommons-mcp/pull/60) | Live library-account mutation boundary                              |
| `clickwheel`               | `9c27552`  | [Merged PR #125](https://github.com/pdugan20/clickwheel/pull/125)    | Client-independent MCP safety plus canonical docs-mirror guidance      |
| `presentations`            | `6f5f2b9`  | [Merged PR #7](https://github.com/pdugan20/presentations/pull/7)     | Lightweight narrative/visual iteration mode                            |
| `rewind`                   | `0fa60c9`  | [Merged PR #182](https://github.com/pdugan20/rewind/pull/182)        | Three canonical shared skills plus live API/data boundaries            |
| `github-automation`        | `5e0f4b5`  | Local only; remote decision pending                                 | Preserves the read-only control-plane invariant                        |
| `github-portfolio-ops`     | `6f38a51`  | Local only; remote decision pending                                 | Historical Superpowers artifacts do not trigger workflow               |

## Generated mirror exception

`clickwheel-fm-docs` is an external-organization, one-way generated mirror of `clickwheel/docs-mintlify`. It must not
be edited directly. After Clickwheel merged, the existing mirror workflow was dispatched and completed successfully.
Mirror commit `5633115` contains `AGENTS.md` and the Claude import shim from Clickwheel merge `9cf8833e`.

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

## Remaining optional decisions

- Decide whether `github-automation` and `github-portfolio-ops` should remain local-only, be archived, or receive
  private remotes before attempting to sync them.
- Retry NextUp MCP OAuth later if that integration is needed. This remains machine-local and must not be committed.
- Use `./scripts/audit-migration-branches.sh --fetch --merged` for future post-merge verification.

## Local environment status and follow-ups

- Codex CLI `0.145.0` is installed and passes a fresh-process exploration-mode smoke test. The stale `supports_reasoning_summaries` model-cache warning and skill-description budget warning no longer appear.
- The Computer Use MCP command now uses its verified absolute executable path. `codex doctor` reports the MCP configuration locally consistent; `scripts/configure-codex.py` applies the same non-secret repair idempotently on other machines when that executable exists.
- The NextUp backend MCP endpoint is configured and advertises OAuth correctly, but authentication is intentionally deferred because the 2026-07-26 browser flow did not complete. No credentials were stored; `codex mcp list` reports `Not logged in`. Retry later with `codex mcp login nextup-mcp-dev`, approve `library:read` and `ugc:write` in the browser, then confirm the listing shows OAuth.
- All applicable checks on all 23 migration pull requests passed before merge. NextUp backend's rerun included documentation quality, pre-commit, Firebase deployment validation, unit coverage, Firebase emulator integration, and the final CI gate. ClaudeLint passed Dogfood and its complete Node/macOS/Linux matrix. ClaudeNotes passed lint, build, tests, database lint/RLS tests, type-drift detection, security, and its final CI gate.
- NextUp backend CI warns that `hashicorp/setup-terraform` still targets deprecated Node.js 20 and is being forced onto Node.js 24. This predates and is unrelated to the agent-workflow migration; update the pinned action separately.
- A fresh Codex `0.145.0` process logs non-blocking validation warnings from bundled OpenAI plugins: the spreadsheet skill's icons escape its asset directory, and template-creator supplies more than three default prompts. These are upstream cache contents, not personal-plugin defects; do not patch generated plugin caches.
- The fresh process also logged transient rollout lookup fallbacks, while `codex doctor` independently reported healthy databases and exact rollout/state-DB parity. Reinvestigate only if thread listing or resume behavior becomes visibly incorrect.
- A no-tool Claude startup loaded about 34.5k context tokens and passed the routing smoke test. Keep configuration smoke tests to one turn; repeated tool turns rewrite/cache that context and cost substantially more.
- Installing `clickwheel/tools/ci` from its lockfile for the repository hook reported 16 existing high-severity npm audit findings. The migration changed no dependencies; investigate separately and do not run `npm audit fix --force` as part of this workflow migration.
