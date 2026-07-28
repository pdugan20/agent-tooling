# Outstanding work

This checklist tracks unfinished setup work. Remove completed items rather than keeping a historical project log here.

## Publish Mintlify Docs for both runtimes

- [ ] Merge the dual-runtime manifest, shared-skill compatibility, packaging, and version-sync changes in
  `pdugan20/mintlify-docs`.
- [ ] Release `mintlify-docs` as `v0.3.0`; confirm both plugin manifests and the release archive report `0.3.0`.
- [ ] Merge the native Codex marketplace catalog in `pdugan20/pdugan20-plugins` and update its Claude marketplace
  entry to `mintlify-docs` `0.3.0`.
- [ ] Merge the desired-state, bootstrap, catalog, and documentation changes in `pdugan20/agent-tooling`.
- [ ] Run both plugin refresh scripts, restart Codex and Claude, and run `./scripts/verify-setup.sh`.
- [ ] Smoke-test one implicit request and one explicit invocation in each runtime.

## Cleanup and portability

- [ ] Run `scripts/setup-new-machine.sh` on the MacBook, restart both products, authenticate required connectors, and
  verify the resulting setup.

NextUp MCP OAuth remains intentionally deferred until its authentication flow is repaired.
