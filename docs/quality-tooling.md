# Quality Tooling

This repository uses a layered quality gate: each tool must cover a distinct defect class, remain reasonably quiet,
and support reproducible installation. Generated catalogs and third-party skill snapshots are validated for
provenance and structure but are not reformatted as locally authored source.

## Adopted checks

| Tool | Role | Policy |
| --- | --- | --- |
| Prettier | JSON, YAML, HTML, CSS, and JavaScript formatting | Exact npm version; check mode in CI |
| Markdownlint | Markdown structure | Exact npm version; repository-specific rule exceptions |
| ClaudeLint | Claude files, skills, and plugin metadata | Exact npm version; strict skill validation |
| Repository validators | Cross-file identity, version, source, and policy invariants | Unit-tested Python |
| Skills CLI | Portable skill discovery and provenance lock generation | Pinned command version in release repositories |
| Ruff | Python linting and formatting | Pinned pre-commit release |
| ShellCheck and shfmt | Shell correctness and formatting | Pinned pre-commit releases |
| actionlint | GitHub Actions syntax and expression semantics | Checksum-pinned binary in CI |
| Gitleaks | Staged and full-history secret scanning | Checksum-pinned binary in CI |
| Typos | Low-noise spelling checks across source and documentation | Version 1.48.0; local and CI gate |
| zizmor | GitHub Actions and Dependabot security analysis | Version 1.28.0; pedantic persona, medium severity and confidence |
| Lychee | External and internal documentation links | Version 0.24.2; scheduled rather than a PR gate because network failures are nondeterministic |

Binary release checksums live in `scripts/install-ci-tools.sh`. GitHub Actions are pinned to full commits and
maintained through Dependabot.

## Deferred tools

| Candidate | Decision |
| --- | --- |
| `skills-ref` | Keep as an occasional compatibility check, not a release gate. The official project describes the reference library as demonstration-only. |
| Agent Ecosystem `skill-validator` | Revisit if skills gain large references or scripts. Its structural checks currently overlap ClaudeLint, the repository validator, and Skills CLI discovery. |
| Taplo | Defer until the repository owns meaningful TOML configuration; `check-toml` already catches syntax errors. |
| yamllint and check-jsonschema | Defer because Prettier, pre-commit syntax hooks, actionlint, ClaudeLint, and repository invariants cover the current YAML and JSON surfaces. |
| Vale or a broad dictionary spell checker | Defer until an editorial style policy is desired. Typos catches objective misspellings with less prose noise. |
| ESLint or Biome | Defer until executable JavaScript or TypeScript becomes a meaningful source surface. |
| Additional dependency scanners | Dependabot and lockfiles are sufficient for the current development-only dependencies. Reassess if this repository ships a runtime or container. |

## Review cadence

Review versions during normal Dependabot maintenance. Re-run this audit when a repository adds a new language,
runtime, package ecosystem, deployment workflow, or large documentation surface; those changes can justify a tool
that would otherwise be redundant.
