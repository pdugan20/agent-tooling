# Outstanding work

This checklist tracks unfinished setup work. Remove completed items rather than keeping a historical project log here.

## Authentication-dependent verification

- [ ] Authenticate the remote Codex MCP servers that need account access: Expo, Sentry, Mintlify Admin, and the four
  protected Cloudflare endpoints. Mintlify Search and Cloudflare Docs are public. Firebase reuses Firebase CLI
  credentials and is already authenticated on the current Mac mini.

## Cleanup and portability

- [ ] Run `scripts/setup-new-machine.sh` on the MacBook, restart both products, authenticate required connectors, and
  verify the resulting setup.

NextUp MCP OAuth remains intentionally deferred until its authentication flow is repaired. Claude and Codex skill
discovery are already verified on the current Mac mini.
