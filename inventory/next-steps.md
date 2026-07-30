# Outstanding work

This checklist tracks unfinished setup work. Remove completed items rather than keeping a historical project log here.

## Authentication-dependent verification

- [ ] Recheck the remote Codex MCP servers with `npm run mcp:check` after product updates and on each new machine.
  Expo, Mintlify Admin, and the four protected Cloudflare endpoints are authenticated on the current Mac mini.
  Mintlify Search and Cloudflare Docs are public, and Firebase reuses Firebase CLI credentials. Sentry authentication
  is blocked by [openai/codex#34684](https://github.com/openai/codex/issues/34684) until Codex preserves the OAuth
  issuer callback parameter.

## Cleanup and portability

- [ ] Run `npm run setup` on the MacBook, restart both products, authenticate required connectors, and
  verify the resulting setup.

NextUp MCP OAuth remains intentionally deferred until its authentication flow is repaired. Claude and Codex skill
discovery are already verified on the current Mac mini.
