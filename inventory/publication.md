# Agent workflow migration publication manifest

Completed: 2026-07-26 through 2026-07-27

The Claude-to-Codex workflow migration is complete for all 23 remote-backed repositories. Every migration was
reviewed through a pull request, passed its applicable checks, and was squash-merged into the repository's default
branch. GitHub then removed every temporary `codex/agent-workflow-migration` remote branch.

Run the durable post-merge audit with:

```bash
npm run migrations:audit -- --fetch --merged
```

That audit verifies each recorded squash-merge commit remains reachable from the current remote default branch and
that no temporary migration branch has reappeared.

## Wave 1: current priorities

| Repository       | PR                                                                 | Migration head | Merge commit |
| ---------------- | ------------------------------------------------------------------ | -------------- | ------------ |
| `nextup-ios-app` | [#772](https://github.com/nxt-up/nextup-ios-app/pull/772)           | `a2eae9f8`     | `2f89c729`   |
| `nextup-backend` | [#740](https://github.com/nxt-up/nextup-backend/pull/740)           | `319117e5`     | `68a6de4a`   |
| `nextup-web`     | [#117](https://github.com/nxt-up/nextup-web/pull/117)               | `fef3229`      | `ae835097`   |
| `pat-portfolio`  | [#87](https://github.com/pdugan20/pat-portfolio/pull/87)            | `fc14e65`      | `7308d50f`   |
| `messenger`      | [#15](https://github.com/pdugan20/messenger-proto/pull/15)          | `02d8f21`      | `9d339b98`   |

## Wave 2: shared skills and operational boundaries

| Repository          | PR                                                                 | Migration head | Merge commit |
| ------------------- | ------------------------------------------------------------------ | -------------- | ------------ |
| `claudelint`        | [#165](https://github.com/pdugan20/claudelint/pull/165)             | `79db2717`     | `016b46d2`   |
| `rewind`            | [#182](https://github.com/pdugan20/rewind/pull/182)                 | `0fa60c90`     | `c0bb6a0a`   |
| `clickwheel`        | [#125](https://github.com/pdugan20/clickwheel/pull/125)             | `9c275528`     | `9cf8833e`   |
| `bibliocommons-mcp` | [#60](https://github.com/pdugan20/bibliocommons-mcp/pull/60)        | `7a9583f7`     | `d04267b7`   |
| `mintlify-docs`     | [#23](https://github.com/pdugan20/mintlify-docs/pull/23)            | `90cab618`     | `222fb1d5`   |
| `presentations`     | [#7](https://github.com/pdugan20/presentations/pull/7)              | `6f5f2b94`     | `d39b9f6c`   |

## Wave 3: repository guidance

| Repository                 | PR                                                                 | Migration head | Merge commit |
| -------------------------- | ------------------------------------------------------------------ | -------------- | ------------ |
| `chat-app-prototype`       | [#78](https://github.com/pdugan20/chat-app-prototype/pull/78)       | `6cb668ef`     | `b81724f3`   |
| `claude-usage`             | [#7](https://github.com/pdugan20/claude-usage/pull/7)               | `f60bb435`     | `f73384ad`   |
| `claudenotes`              | [#64](https://github.com/pdugan20/claudenotes/pull/64)              | `8e997b7b`     | `ee21f276`   |
| `e-ink-scoreboard`         | [#84](https://github.com/pdugan20/e-ink-scoreboard/pull/84)         | `825d5444`     | `2ee6682f`   |
| `figma-chat-builder`       | [#96](https://github.com/pdugan20/figma-chat-builder/pull/96)       | `82a0a6f6`     | `93e77b92`   |
| `figma-music-injector`     | [#38](https://github.com/pdugan20/figma-music-injector/pull/38)     | `e08ddca0`     | `6f842d81`   |
| `imessage-swift-prototype` | [#5](https://github.com/pdugan20/imessage-swift-prototype/pull/5)   | `936dcd79`     | `fe5a878e`   |
| `libby-downloader`         | [#123](https://github.com/pdugan20/libby-downloader/pull/123)       | `51f00881`     | `9c9ac844`   |
| `passant-prototype`        | [#65](https://github.com/pdugan20/passant-prototype/pull/65)        | `223d62cf`     | `739d7f93`   |
| `rss-feed-generator`       | [#42](https://github.com/pdugan20/rss-feed-generator/pull/42)       | `671127a2`     | `de98a45a`   |
| `touchpoint`               | [#9](https://github.com/pdugan20/touchpoint/pull/9)                  | `6376a64c`     | `8a823933`   |
| `x-archive`                | [#62](https://github.com/pdugan20/x-archive/pull/62)                | `0553ea9d`     | `712e3705`   |

## Final verification notes

- All applicable pull-request checks passed before merge. This included the larger NextUp, ClaudeLint, ClaudeNotes,
  Clickwheel, and Expo/React Native matrices.
- ClaudeLint keeps its portable shared skill free of runtime-specific metadata. A path-specific override disables
  only ClaudeLint's Claude-only `skill-missing-version` rule for that canonical shared skill.
- Mintlify Docs, ClaudeNotes, and X Archive wrap two shared work-mode bullets to satisfy their Markdown line-length
  rules; the wording is unchanged.
- ClaudeNotes was replayed over the newer `main` image-upload hardening commit before its PR was opened.
- The generated `clickwheel-fm/docs` mirror was synchronized through its existing one-way workflow. Mirror commit
  `5633115` contains the inherited `AGENTS.md` and Claude import shim; no direct mirror edit or PR was made.
- Primary-checkout work-in-progress and the two pre-existing NextUp backend recovery stashes were preserved.

## Deliberate exclusions and remaining optional work

- `github-automation` (`5e0f4b5`) and `github-portfolio-ops` (`6f38a51`) remain local-only. Creating GitHub remotes or
  archiving them is a separate decision.
- NextUp MCP OAuth remains intentionally deferred. No credentials were stored; retry with
  `codex mcp login nextup-mcp-dev` and then confirm `codex mcp list` reports OAuth authentication.
- Existing dependency/security findings reported by repository tooling were not changed because these migrations
  did not modify dependencies. Track remediation separately rather than using forced audit fixes.
- The NextUp backend's deprecated Node.js action warning and non-blocking validation warnings from bundled OpenAI
  plugin caches remain independent maintenance items.
