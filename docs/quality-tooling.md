# Quality tooling

Repository checks cover source quality, provenance, and configuration contracts. They do not establish that a
signed-in desktop chat can use every selected capability. Run `npm run verify` for the repository gate and the
[setup checks](setup.md#current-command-boundary) separately for installed configuration.

## Checks used here

| Tool | Role | Version source |
| --- | --- | --- |
| Prettier | Catalog code and configuration formatting | `package.json` and `package-lock.json` |
| Markdownlint | Maintained Markdown structure | `package.json` and `.markdownlint.json` |
| TypeScript | Catalog type checks | `package.json` and catalog tsconfig files |
| ClaudeLint | Retained Claude configuration checks and explicit strict validation of selected skill snapshots | `package.json`, `.claudelintrc.json`, and `lint:claude` |
| Repository validators and tests | Source, version, link, plugin, configuration, release, and dependency-policy contracts | `scripts/` |
| Ruff | Python linting and formatting | `.pre-commit-config.yaml` |
| ShellCheck and shfmt | Shell correctness and formatting | `.pre-commit-config.yaml` |
| actionlint and zizmor | Workflow syntax and security analysis | `scripts/install-ci-tools.sh` |
| Gitleaks | Staged and full-history secret scanning | `scripts/install-ci-tools.sh` |
| Typos | Low-noise spelling checks | `scripts/install-ci-tools.sh` |
| Lychee | Scheduled internal and external link checks | `scripts/install-ci-tools.sh` and `.lychee.toml` |

`npm run verify` runs unit tests, catalog drift detection, pre-commit checks, full-history secret scanning, and
whitespace checks. Catalog compilation has its own `npm run catalog:build` command.
Snapshots are excluded from blanket formatting and Markdown rewrites. They are still subject to provenance policy
and the explicit ClaudeLint skill-validation command. This compatibility check is not proof of Codex runtime behavior.

## Checks in publishing repositories

Skills CLI records installed skill provenance here. The Skills repository owns its portable-skill validation and
behavioral evaluation. Plugin publishers own manifest validation and installation smoke tests for their supported
clients. Claude's validator and Codex's creator workflows are relevant to those packages; they are not interchangeable
universal validators. See [authoring](authoring.md).

## Dependency updates

Renovate owns npm and GitHub Actions update PRs under [`renovate.json`](../renovate.json).
Dependabot's retained configuration sets its update PR limits to zero. Reviewed Renovate rules permit selected
minor and patch updates to merge after required checks; major and other exceptional changes need dashboard approval.
This does not authorize automatic instruction, plugin, or skill updates.

GitHub Actions use full commit pins. Exact tool versions and checksums live in the configuration and installer files
above; documentation does not maintain a second version inventory.

## Deferred checks

| Candidate | Current decision |
| --- | --- |
| `skills-ref` | Occasional compatibility check; not an additional release gate |
| Taplo | TOML syntax checks cover the current surface; revisit when richer TOML policy is needed |
| yamllint and check-jsonschema | Add only when they catch gaps left by existing syntax, workflow, and contract checks |
| Vale or a broad dictionary | Typos handles objective spelling errors; broader editorial enforcement remains optional |
| ESLint or Biome | Reassess against concrete catalog lint gaps; current checks include types, formatting, and tests |
| Additional dependency scanners | Reassess if this private tooling repository starts distributing a runtime or container |

Review the gate when adding a language, runtime, distribution channel, or new defect class. Keep each check's
scope explicit, especially while Claude runtime support becomes optional.
