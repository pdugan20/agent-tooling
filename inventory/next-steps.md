# Outstanding work

This checklist tracks unfinished setup work. Remove completed items rather than keeping a historical project log here.

## Authentication-dependent verification

- [ ] Sign in to Claude Code on the current machine, start a fresh process, and smoke-test one implicit request plus
  one explicit `mintlify-docs:review-docs` invocation. Static plugin discovery and strict validation pass at `0.3.0`;
  live invocation is blocked only because `claude auth status` reports `loggedIn: false`. Codex passed both invocation
  paths on July 28, 2026.

## Cleanup and portability

- [ ] Run `scripts/setup-new-machine.sh` on the MacBook, restart both products, authenticate required connectors, and
  verify the resulting setup.

NextUp MCP OAuth remains intentionally deferred until its authentication flow is repaired.
