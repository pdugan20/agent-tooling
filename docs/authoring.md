# Skill and plugin authoring

Use the narrowest validator for the artifact, then run the repository's complete verification command before
publishing. Static checks prove structure and policy compliance; they do not prove that a skill triggers correctly or
produces a useful result.

## Tool matrix

| Artifact | Primary checks | Formatting and supporting checks | Where used |
| --- | --- | --- | --- |
| Patrick-owned skill | Codex `$skill-creator` quick validation; ClaudeLint strict validation; Skills CLI discovery | Markdownlint; ShellCheck and shfmt for shell resources; Ruff for Python resources | `patrick-workflows` |
| Locked skill snapshot | Official Skills CLI lock and update review | No local rewriting; repository policy checks provenance, source path, release ref, compatibility links, and known duplicate overrides | `agent-tooling/.agents/skills` |
| Claude plugin | `claude plugin validate . --strict`; ClaudeLint `validate-plugin` | Markdownlint, JSON/YAML formatting, package and install smoke tests | `mintlify-docs` and `patrick-tools` |
| Codex plugin | Codex `$plugin-creator` validation | JSON formatting plus a marketplace install/reinstall smoke test | `mintlify-docs` and `patrick-tools` |
| Claude marketplace | ClaudeLint `validate-plugin --preset strict --warnings-as-errors` | JSON formatting and dependency-install smoke test | `patrick-tools` CI |
| Codex marketplace | Codex `$plugin-creator` generation/validation and live install smoke test | JSON syntax validation; source tag and policy review | `patrick-tools` CI and release review |
| GitHub Actions | actionlint and zizmor | Prettier for YAML; full commit pins | All four maintained repositories |
| Repository scripts | ShellCheck and shfmt for shell; Ruff for Python; Prettier for JavaScript/JSON/YAML | Unit tests for behavior | `agent-tooling` verification |
| Secrets and credentials | Gitleaks staged and full-history scans | Manual review of generated archives and runtime snapshots | `agent-tooling` pre-commit, pre-push, and CI |

## Commands already incorporated

For shared agent tooling:

```bash
npm run lint:claude
npm run lint:markdown
npm run format:check
npm run verify
```

`npm run verify` is the complete local and GitHub Actions gate. It runs unit tests, catalog drift detection,
pre-commit validators, repository policy checks, and secret scanning. ClaudeLint validates the managed skill tree
while repository policy applies first-party invocation rules. All snapshots remain immutable in this consumer.

The Agent Skills specification permits only its portable frontmatter fields. Some upstream packages intentionally
include agent-specific fields such as Claude's `context: fork` or `disable-model-invocation`; the official `skills`
CLI does not transform those fields for Codex. Keep locked upstream snapshots unmodified and treat that validator
output as a compatibility warning to review, not a reason to fork the skill. Apply runtime policy through
`agents/openai.yaml`, Claude `skillOverrides`, or repository instructions when the source already supports that
separation.

For Mintlify Docs:

```bash
npm run verify
npm audit
```

Its verification command runs strict ClaudeLint, Markdownlint, ClaudeLint's marketplace/plugin checks, and Claude
Code's official plugin validator. CI additionally runs the install smoke test, ShellCheck, Ruff, actionlint, Typos,
and zizmor; Lychee runs on a network-dependent schedule.

For the marketplace repository, CI validates both catalogs and installs every published plugin in its supported
runtimes. A successful install is the final packaging check because it exercises the same catalog and cache path
users receive.

## Built-in authoring workflows

Use `$skill-creator` when creating or substantially revising a skill. It provides the supported scaffold,
`agents/openai.yaml` generation, frontmatter/name validation, and forward-testing guidance. Ask it to run its bundled
`quick_validate.py`; do not hardcode the system skill's machine-specific filesystem path in repository scripts.
If the bundled Python validator reports that `yaml` is unavailable, run it through an ephemeral environment such as
`uv run --no-project --with pyyaml python <validator-script> <artifact-path>` rather than modifying system Python.

Use `$plugin-creator` for a Codex plugin or marketplace entry. It provides the supported manifest shape, marketplace
policy fields, schema validator, and cache-buster/reinstall flow. The Codex validator currently ships with that
built-in workflow rather than as a stable standalone CI command, so run it before publishing and retain the live
install smoke test in CI.

## What static tooling cannot prove

- whether a description triggers on the prompts you actually use;
- whether an automatic skill stays out of lightweight exploration when it should;
- whether an explicit-only skill remains discoverable when named;
- whether instructions produce a good result in SwiftUI, React Native, React, a browser, or a simulator; and
- whether a plugin update behaves correctly after runtime caching and restart.

For those, forward-test representative implicit and explicit prompts in a new task. For design workflows, inspect the
result in the actual browser or simulator. For a plugin release, reinstall from the published marketplace, restart the
runtime, and smoke-test at least one automatic and one explicit invocation.
