# Skill and plugin authoring

For maintainers changing reusable instructions or packaging. Author Patrick-owned skills in
[Skills](https://github.com/pdugan20/skills); this repository consumes reviewed snapshots.
Use the narrowest checks first, then the owning repository's full verification before publishing.

## Choose the artifact

| Artifact | Checks and ownership |
| --- | --- |
| Patrick-owned skill | Author in Skills; use `$skill-creator`, source-repository policy, portable validation, and representative runtime prompts |
| Locked skill snapshot | Install through Skills CLI; review source, ref, content, and lock diff; do not rewrite it here |
| Codex plugin or marketplace | Validate supported manifests and metadata, then test installation and discovery in the intended client |
| Optional Claude plugin or marketplace | Run Claude's validator and install checks in its owning repository |
| Repository scripts | Unit tests plus Ruff, ShellCheck, shfmt, or JavaScript checks appropriate to the language |
| GitHub Actions | actionlint, zizmor, pinned actions, and repository policy |
| Credentials | Keep out of artifacts; Gitleaks checks staged changes and full history |

## Author for current Codex

Use portable `SKILL.md` content for the workflow. Put Codex interface metadata, dependencies, and invocation policy
in `agents/openai.yaml`. Make trigger descriptions concise and put the main use case first: Codex can shorten the
initial skill list when many capabilities are installed. [Official skills guide](https://learn.chatgpt.com/docs/build-skills)

Use `$skill-creator` when creating or substantially revising a skill. Run its available validator, without hardcoding
its machine-specific path into repository scripts. If the required creator is unavailable, follow the shared
agreement's missing-skill rule instead of claiming an equivalent workflow ran.

Current plugin guidance prefers portable root `plugin.json` and `mcp.json`, with OpenAI-specific settings under
`extensions.com.openai`. Existing `.codex-plugin/plugin.json` packages remain supported. The built-in plugin creator
may scaffold that compatibility layout; review its output against the current target surface.
[Official packaging guidance](https://developers.openai.com/plugins/build/plugins)

Use `$plugin-creator` when available for Codex-specific scaffolding and validation. A successful schema check does not
prove installation, authentication, tool availability, or invocation. Test the published package's actual install path.
Lifecycle hooks need separate compatibility, trust, and event checks; manually installed desktop plugins and public
directory submissions have different constraints. [Official hooks guidance](https://learn.chatgpt.com/docs/hooks)

Claude-specific frontmatter and plugin components need a separate compatibility review. Do not alter locked
snapshots to satisfy a different harness's schema. Apply supported runtime policy or fix the canonical source.
See [invocation controls](skill-invocation.md) and [plugin migration](https://developers.openai.com/plugins/guides/submit-claude-plugin).

## Verify changes here

```bash
npm run lint:markdown
npm run verify
```

The full gate runs tests, catalog drift checks, pre-commit validators, repository policy, and secret scanning.
`lint:claude` checks Claude configuration files only. Skill content is validated where it is authored: Patrick-owned
skills in Skills before release, and third-party skills upstream. Here, the snapshot hash check confirms each locked
snapshot is unmodified.
See [setup](setup.md#develop-this-repository) for prerequisites and [quality tooling](quality-tooling.md) for scope.

## Check behavior in the runtime

For an affected skill, start a fresh chat and try a matching prompt, an explicit invocation, and a negative prompt
that should not trigger it. Preserve explicit-only planning, TDD, worktrees, orchestration, and image-generation
boundaries. Check that publication and live-data actions still require the existing authorization.

For a plugin, check the installed source, enabled state, skill discovery, MCP availability, and any hook trust review.
For UI work, inspect the browser or simulator result. A catalog entry or static validator does not establish useful
behavior, effective availability, or performance.
