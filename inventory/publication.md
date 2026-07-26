# Agent workflow migration publication manifest

Audit date: 2026-07-26

This is the durable publication record for the Claude-to-Codex workflow migrations. Branch pushes and Wave 1 draft pull requests were authorized and completed on 2026-07-26. It does not authorize merges or opening later-wave pull requests.

## Verified preflight state

- Branch: `codex/agent-workflow-migration` in every remote-backed repository.
- All 23 remotes were fetched immediately before this manifest was written.
- Every migration branch is exactly one commit ahead of, and zero commits behind, its current remote default branch.
- Each migration commit's parent is the merge base with the current remote default branch.
- All 23 reviewed branch SHAs now exist remotely as `codex/agent-workflow-migration` and exactly match the local migration commits.
- No rebase or conflict repair is currently required.
- The large NextUp skill diffs remove duplicated `.claude/skills` payloads after preserving the canonical `.agents/skills` copies. No canonical skill resource is deleted.
- NextUp backend keeps `.claude/skills/BEST-PRACTICES.md` as a compatibility symlink to the canonical `.agents/skills/README.md` so archived documentation links remain valid.
- Primary-checkout work-in-progress is not part of these branches.

Because remote state can change, rerun the post-publication SHA and divergence checks when resuming this migration.

```bash
./scripts/audit-migration-branches.sh --fetch --published
```

## Publication waves

All remote-backed branches are pushed. Pull requests are being opened in waves so review and notifications stay manageable.

### Wave 1: current priorities

| Repository       | Default  | Head       | Suggested PR title                          | Scope                                       |
| ---------------- | -------- | ---------- | ------------------------------------------- | ------------------------------------------- |
| `nextup-ios-app` | `main`   | `a2eae9f8` | `chore: share agent skills across runtimes` | 19 canonical skills and Claude symlinks     |
| `nextup-backend` | `main`   | `319117e5` | `chore: share agent skills across runtimes` | 24 canonical directories, safety, MCP docs  |
| `nextup-web`     | `main`   | `fef3229`  | `docs: align agent workflows`               | Exploration mode and Firebase boundaries    |
| `pat-portfolio`  | `main`   | `fc14e65`  | `docs: align agent workflows`               | Portfolio design-iteration guidance         |
| `messenger`      | `master` | `02d8f21`  | `docs: align agent workflows`               | Expo design iteration and opt-in strict TDD |

Published as draft pull requests: [iOS #772](https://github.com/nxt-up/nextup-ios-app/pull/772), [backend #740](https://github.com/nxt-up/nextup-backend/pull/740), [web #117](https://github.com/nxt-up/nextup-web/pull/117), [portfolio #87](https://github.com/pdugan20/pat-portfolio/pull/87), and [Messenger #15](https://github.com/pdugan20/messenger-proto/pull/15).

All applicable Wave 1 checks passed on 2026-07-26. The backend compatibility-symlink rerun passed documentation quality, pre-commit, Firebase deployment validation, unit coverage, Firebase emulator integration, and the final CI gate.

### Wave 2: shared skills and operational boundaries

| Repository          | Default | Head      | Suggested PR title                            | Scope                                             |
| ------------------- | ------- | --------- | --------------------------------------------- | ------------------------------------------------- |
| `claudelint`        | `main`  | `3b48ca4` | `chore: share agent guidance across runtimes` | Nested guides and one shared skill                |
| `rewind`            | `main`  | `0fa60c9` | `chore: share agent guidance across runtimes` | Three shared skills and live-data boundaries      |
| `clickwheel`        | `main`  | `9c27552` | `chore: share agent guidance across runtimes` | Client-neutral MCP safety and mirror-source guide |
| `bibliocommons-mcp` | `main`  | `7a9583f` | `chore: share agent guidance across runtimes` | Live library-account mutation boundary            |
| `mintlify-docs`     | `main`  | `9eb14ed` | `chore: share agent guidance across runtimes` | Cross-runtime contributor context for plugin work |
| `presentations`     | `main`  | `6f5f2b9` | `chore: share agent guidance across runtimes` | Lightweight narrative and visual iteration        |

### Wave 3: low-risk repository guidance

| Repository                 | Default  | Head      |
| -------------------------- | -------- | --------- |
| `chat-app-prototype`       | `main`   | `6cb668e` |
| `claude-usage`             | `main`   | `f60bb43` |
| `claudenotes`              | `main`   | `5c5d6d4` |
| `e-ink-scoreboard`         | `main`   | `825d544` |
| `figma-chat-builder`       | `main`   | `82a0a6f` |
| `figma-music-injector`     | `main`   | `e08ddca` |
| `imessage-swift-prototype` | `main`   | `936dcd7` |
| `libby-downloader`         | `main`   | `51f0088` |
| `passant-prototype`        | `master` | `223d62c` |
| `rss-feed-generator`       | `main`   | `671127a` |
| `touchpoint`               | `master` | `6376a64` |
| `x-archive`                | `main`   | `0c2696c` |

Use `chore: share agent guidance across runtimes` as the Wave 3 PR title.

## Pull request body template

```markdown
## Summary

- Make `AGENTS.md` the canonical repository guidance for Codex and other compatible agents.
- Keep Claude on the same source through a small import shim or per-skill symlinks.
- Default lightweight UI, design, documentation, and prototype work to exploration mode.
- Keep strict TDD, formal plans, production hardening, deployments, and live-data mutations explicit and proportional to the request.

## Why

This removes runtime-specific instruction drift while preserving repository-specific architecture and safety rules. Claude and Codex now consume the same maintained source instead of two hand-edited copies.

## Verification

- Branch is one commit ahead of and zero commits behind the current default branch.
- `git diff --check` passes.
- Repository hooks or focused format/lint checks passed where configured.
- Fresh Codex and Claude processes both selected exploration mode for a quick UI experiment without requiring a spec, worktree, or TDD.

## Notes

- No application runtime behavior, deployment, production data, credentials, or repository settings changed.
- Large deletion counts in skill-heavy repositories are removal of duplicated Claude payloads; canonical `.agents/skills` resources remain present.
```

Add repository-specific verification to the template where available. `figma-chat-builder` ran TypeScript checks and 88 tests; all four newly shared skills passed the Codex skill validator; Clickwheel's configured formatting, Markdown, and commit hooks passed.

## Exclusions and separate decisions

- `clickwheel-fm-docs` is a generated mirror and must not receive a direct PR. The `clickwheel` source migration carries nested docs guidance through the existing mirror workflow after merge.
- `github-automation` (`5e0f4b5`) and `github-portfolio-ops` (`6f38a51`) are local-only. Decide whether to archive them, keep them local, or create private remotes.
- `agent-tooling` is published as the private repository `pdugan20/agent-tooling`.
- NextUp MCP OAuth credentials are machine-local and never belong in a repository or this manifest.

## Final publication gate

Before each push:

1. Fetch `origin` and require the migration branch to remain zero commits behind the remote default branch.
2. Confirm the remote migration branch still does not exist.
3. Confirm the primary checkout's existing work remains unchanged.
4. Push the exact local migration branch without force.
5. Open a pull request; do not merge automatically.

After each merge, fetch the canonical checkout and verify a fresh Codex and Claude session sees the merged guidance from the default branch.
