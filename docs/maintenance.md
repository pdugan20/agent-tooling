# Maintenance

`agent-tooling` is the canonical consumer configuration for Patrick's shared instructions, locked skill set,
desired plugin state, and configured Superpowers baseline. Patrick-owned skills are released from
`pdugan20/skills`; Claude and Codex consume the installed snapshots through runtime-specific symlinks.

## Update shared instructions

1. Edit the canonical file in this repository.
2. Validate affected skills with `quick_validate.py` and run the repository's configuration tests.
3. Regenerate the catalog when skill metadata or plugin state changes.
4. Commit and push this repository.
5. On another machine, pull, run `npm run bootstrap`, and start a new Claude or Codex task.

## Update Patrick workflows

1. Edit and validate the canonical skill in `pdugan20/skills`.
2. Release a new semantic version there.
3. Install that exact tag in this repository with the Skills CLI for Codex and Claude Code.
4. Review `.agents/skills/`, `.claude/skills/`, and `skills-lock.json`.
5. Regenerate the catalog, run `npm run bootstrap`, and start new tasks.

## Update upstream skills

The seven third-party skills in `.agents/skills/` are project-scoped installations managed by the official
[`skills` CLI](https://github.com/vercel-labs/skills). Their exact GitHub sources and content hashes live in
`skills-lock.json`; the repository does not maintain hand-copied versions under `skills/`.

```bash
npm run skills:update
git diff -- .agents/skills .claude/skills skills-lock.json
npm run verify
```

Review instruction changes like dependency changes: confirm their source, inspect the full diff, and smoke-test the
affected workflow before committing. Do not patch the generated snapshot, run a global update for this repository,
or auto-merge instruction updates. If a personal customization is genuinely needed, create a clearly named skill in
Skills instead of silently diverging the upstream copy.

Updates remain intentionally manual for now. The CLI provides the canonical install, lock, and update operation but
does not provide a first-party scheduled pull-request workflow. Adding custom branch and pull-request automation
would recreate tooling around the official updater, so revisit this only if the CLI ships a supported automation
path. The current maintenance command is short, reviewable, and safe to run alongside other dependency updates.

The upstream `swiftui-pro` package includes a nested Claude compatibility copy inside its canonical Codex-ready
skill directory. The snapshot remains unmodified so `skills-lock.json` can track it exactly; `bootstrap.sh` uses
Codex's supported per-skill configuration override to disable only that nested duplicate. Rerun bootstrap after an
upstream update so the override follows the current checkout location.

## Verify repository changes

Install the repository development dependencies once as documented in `README.md`, then run:

```bash
npm run verify
```

This is the exact `ci` status check used by GitHub Actions. It validates the canonical files and repository policy
without inspecting authenticated runtime state. Continue to use `npm run setup:check` separately after applying the
setup on a real machine.

ClaudeLint is intentionally strict for workflows maintained in this repository. Locked upstream snapshots are
excluded from local style rewrites and lint policy; their integrity and provenance are enforced through
`skills-lock.json`. `scripts/validate_repository.py` separately validates that split, the configured Superpowers
baseline, and desired plugin state.

### Secret scanning

GitHub secret scanning and repository push protection are enabled. Gitleaks remains an independent defense-in-depth
check at three points:

- staged changes in the local pre-commit hook;
- full Git history in the local pre-push hook;
- full Git history in required GitHub Actions `ci` and release verification.

Install both local hooks with `pre-commit install --hook-type pre-commit --hook-type pre-push`. CI checkouts must retain `fetch-depth: 0`; repository policy validation guards that invariant.

## Release agent tooling

GitHub releases describe the complete repository setup and use ordinary SemVer tags. `package.json` is the
repository version source. The Superpowers fork is versioned in its own repository and is not coupled to this
repository's release number.

1. Move the completed entries from `[Unreleased]` into a dated version section in `CHANGELOG.md`.
2. Bump the root `package.json` version according to SemVer and refresh `package-lock.json`.
3. Run `npm run verify` and merge the verified change to `main`.
4. Create and push an annotated repository tag from that merge commit, substituting the release version:

   ```bash
   VERSION=0.4.0
   git tag -a "v$VERSION" -m "v$VERSION"
   git push origin "v$VERSION"
   ```

5. Confirm the release workflow created the matching GitHub Release with the curated changelog notes.
6. On each machine, pull and rerun the relevant bootstrap or refresh commands from the release's upgrade notes.

The release workflow rejects malformed tags, tags that differ from the root package version, and versions without a
changelog section. It publishes release notes only; it does not publish an npm package, update runtime caches, or
install plugins on other machines.

## Maintain the catalog

The committed `catalog/data.json` file is generated from skill frontmatter, plugin manifests, desired plugin lists,
and `catalog/plugin-metadata.json`. Do not hand-edit it.

```bash
npm run catalog:generate
npm run catalog
```

When a configured third-party plugin changes, update its short descriptive metadata only if the existing description
or canonical source URL is no longer accurate. Skill and plugin source labels link to GitHub whenever the canonical
source is public; Codex-managed bundles remain plain text unless OpenAI publishes a repository for them. CI runs
`npm run catalog:check` and fails when generated data drifts from canonical inputs.

Assign a stable `capabilityId` when Codex and Claude use different package IDs for the same logical integration. The
catalog then renders one capability row with per-app package ID, delivery method, version, and state. Keep
semantically different capabilities separate even when their names are related—for example, Mintlify and Mintlify
Docs remain distinct.

For a machine-local runtime comparison, run `npm run catalog:snapshot`. The resulting
`catalog/runtime-data.local.json` contains only capability identifiers, versions, runtime state, and repository
metadata—not installation paths, credentials, or plugin configuration—and is ignored by Git.

## Refresh installed Codex plugins

### Choose a plugin source

Prefer a vendor-maintained Git marketplace when the vendor package explicitly supports Codex and provides the full
capability without losing a Codex-connected app. Use a Codex-curated package when it adds material app integration or
Codex-specific compatibility. Use one active source per plugin, and never fill a version gap by copying individual
plugin skills into this repository.

Review direct packages for hooks, telemetry, authentication changes, manifest compatibility, removed capabilities,
and skill-name collisions before changing this split. A higher version alone is not enough. The manifests and
catalog metadata record the current source decisions without duplicating them here.

Run:

```bash
npm run plugins:refresh:codex
```

This command does not install or refresh `config/codex-managed-plugins.txt`. Codex owns that account/workspace layer;
use the Plugins tab to install missing entries and inspect their current versions. Do not add CLI copies of those
plugins to compensate for a missing or delayed UI installation.

The script refreshes Git marketplace snapshots, re-adds every configured plugin in place, reapplies the Product Design skill overrides, and reminds you to start a new task. Re-adding an installed plugin refreshes its recorded version without an uninstall. OpenAI-curated and bundled local marketplaces are refreshed by Codex application or CLI updates; the add uses whichever snapshot that installation currently exposes.

The installer also removes retired and superseded CLI plugin state through `codex plugin remove`, including orphaned
caches from personal or removed marketplaces. Shared marketplaces may retain inert downloaded package caches after
removal; `codex plugin list --json` and the Plugins tab determine active installed state. `npm run setup:check`
fails if a retired plugin, an unconfigured Superpowers copy, or a duplicate managed plugin remains installed.
Account-managed plugins listed in
`config/codex-managed-plugins.txt` must be checked in the Codex Plugins tab because the CLI does not authoritatively
report that separate layer.

The current Codex CLI has no `plugin update` command. Its relevant refresh primitives are `codex plugin marketplace upgrade` and `codex plugin add`.

`mintlify-docs` is refreshed from the native Codex catalog in `pdugan20/plugins`. Its canonical plugin code
lives in `pdugan20/mintlify-docs`; update and release that repository first, then refresh the marketplace snapshot and
re-add the configured plugin here.

Refresh the desired Claude plugin set with:

```bash
npm run plugins:refresh:claude
```

Underneath, this runs `claude plugin marketplace update` and `claude plugin update` for the entries in `config/claude-plugins.txt`. Claude requires a restart after a plugin update.

`npm run setup:check` requires the enabled user-scoped Claude set to match that manifest exactly, ignoring only
skill-directory compatibility records. Installation and refresh use Claude's official `plugin disable` command to
turn off undeclared user-scoped plugins without uninstalling them. Add a capability deliberately to the manifest
before refreshing when it should remain part of the shared setup.

Capabilities needed by only one repository belong with that repository instead of this global manifest. For
example, `rss-feed-generator` pins Railway's canonical `use-railway` Agent Skill once under `.agents/skills` and
links it into Claude. This gives both agents the same project-scoped source without installing either runtime's
Railway plugin globally.

The Claude and Codex installations of `mintlify-docs` use the same tagged source release. The source repository keeps
separate `.claude-plugin` and `.codex-plugin` manifests only for runtime packaging; both manifests point at the same
`skills/` directory and are versioned together.

## Update the configured Superpowers fork

The actual Superpowers plugin is installed from [`pdugan20/superpowers`](https://github.com/pdugan20/superpowers),
a thin fork of [`obra/superpowers`](https://github.com/obra/superpowers). The fork keeps an `upstream` Git remote and
documents its intentionally small patch set in `CUSTOMIZATION.md`. `config/superpowers.json` is this repository's
machine-readable record of the installed baseline.

Run `npm run superpowers:check` at any time. A weekly GitHub Actions job runs the same comparison and opens one issue
when upstream `main` advances.

To update safely:

1. In the fork checkout, fetch `upstream` and review the commits since `config/superpowers.json`'s
   `upstreamCommit`.
2. Merge or rebase the new upstream version into a branch of the fork. Resolve conflicts by preserving the three
   policy patches documented in `CUSTOMIZATION.md`; do not copy upstream over the fork wholesale.
3. Bump the fork to `<upstream-version>-config.<revision>` and update both plugin manifests and marketplace entries.
4. Run the fork's configured-policy test, Codex packaging tests, hook tests, version check, and
   `claude plugin validate .`.
5. Push the fork, then update `upstreamVersion`, `upstreamCommit`, and `forkVersion` in
   `config/superpowers.json`. Regenerate the catalog and run `npm run verify` here.
6. Run `npm run plugins:refresh:codex` and `npm run plugins:refresh:claude`, restart both products, and run
   `npm run setup:check`.
7. Start new tasks and smoke-test one automatic workflow (for example debugging) plus negative prompts for TDD,
   brainstorming, worktrees, and the browser option picker.

Because plugin cache paths can include versions, rerun `npm run bootstrap` after a Codex or Product Design update,
then start a new task so the configured skill overrides point at the current installation.
