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

## Update Patrick skills

1. Edit and validate the canonical skill in `pdugan20/skills`.
2. Release a new semantic version there.
3. Install that exact tag in this repository with the Skills CLI for Codex and Claude Code.
4. Review `.agents/skills/`, `.claude/skills/`, and `skills-lock.json`.
5. Regenerate the catalog, run `npm run bootstrap`, and start new tasks.

Before updating this consumer, complete the release from the `pdugan20/skills` repository, including its
`npm run refresh:skills-sh` and `npm run check:skills-sh` publication checks. The GitHub tag is the exact installed
source; skills.sh is a separately indexed discovery page and can remain stale after GitHub changes until its refresh
finishes.

Use the tag URL form; `owner/repository@tag` is parsed as a skill selector by current Skills CLI releases:

```bash
npx skills add https://github.com/pdugan20/skills/tree/vX.Y.Z --agent codex claude-code --skill '*' -y
```

## Update upstream skills

The third-party skills in `.agents/skills/` are project-scoped installations managed by the official
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

Claude has no equivalent fix, so it lists both `swiftui-pro` and `swiftui-pro:swiftui-pro`. Claude loads the
directory as the plugin `swiftui-pro@skills-dir`, because it contains `.claude-plugin/plugin.json`. The nested copy
is older than the top-level skill. Measured on 2026-09-17 from the `skills` list in a headless `stream-json` init
event:

- `skillOverrides` with the key `swiftui-pro:swiftui-pro` changes nothing.
- `skillOverrides` with the key `swiftui-pro` hides the newer top-level copy and keeps the stale one.
- `enabledPlugins` with `swiftui-pro@skills-dir` set to `false` hides both copies.

Leave the duplicate in place. Do not edit the snapshot to remove it. The same package shape affects
`swift-testing-pro` in repositories that lock it.

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

The local snapshot excludes Codex-owned bundled and primary-runtime packages. Those packages are supplied with the
active Codex runtime rather than selected or maintained by this repository, so listing them as ordinary catalog
capabilities adds noise without describing Patrick's tooling choices.

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

Patrick's Mintlify skills are installed from the same tagged `pdugan20/skills`
release as the design and delivery skills. The separate `mintlify-docs` plugin is
retired and removed by the install and refresh scripts. Mintlify's official
plugin remains installed for current product mechanics.

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

The `.agents/skills/` snapshots and `.claude/skills/` compatibility links give
both runtimes the same Patrick-owned skill contents without a second plugin
installation.

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

## Read-only skill freshness and usage

Run `npm run skills:check` before deciding what to update. It compares installed
skill files with their declared Git source in disposable temporary checkouts,
without changing snapshots, locks or runtime links. The machine-local report is
`catalog/skill-freshness.local.json` and records the check time, resolved commit,
comparison hashes, source/ref and status for every selected standalone skill.

- `current` means the files match the checked default branch.
- `pinned-ref-verified` means they match the selected tag/commit; it does not mean
  there is no newer release. Review upstream releases before advancing a pin.
- `source-differs` means the source and installation differ; inspect both before
  deciding whether this is an update, a local change or an installer discrepancy.
- `unknown` means verification failed. Never display it as current.

Comparison hashes normalize the installer's excluded `metadata.json` and Python
cache directories, and follow in-skill symlinks to match the installer’s materialized copies. Escaping or cyclic links fail verification. They are separate from the CLI's opaque `computedHash`:
registry downloads and Git installations can produce different lock hashes.
The official lock remains the install provenance; comparison hashes do not
replace it. Upstream retrieval errors fail the command and preserve an explicit
unknown result, rather than assuming a skill was deleted.

Skills CLI 1.5.21 aliases `skills check` to its updating operation. Do not use that
command for read-only monitoring. Continue to use the official CLI for deliberate
installations and updates; inspect instruction changes and rerun repository tests
before bootstrapping. The catalog displays the declared ref and CLI content hash
for selected skills. A moving-branch source link is a source reference, not proof
of an immutable revision.

After an approved skill change, run `npm run catalog:generate`, `npm run bootstrap`,
`npm run catalog:snapshot` and `npm run setup:check`; start a new agent task. The
local runtime snapshot lists machine-installed capabilities separately from the
portable selected inventory. Refresh plugin packages through their existing
runtime-specific commands, not through the standalone skills updater. Account
managed Codex plugins remain subject to the app's inventory limitations.

Review freshness monthly and after a framework or plugin upgrade. This is a
maintenance cadence, not an installed background scheduler. Do not auto-merge
instruction changes or automatically enable newly introduced skills.

For each substantial task, record the skills actually invoked with its evidence
in the task or issue. The installed catalog is not a usage log. Project-specific
profiles should link to this inventory, explain routing and exclusions, and avoid
copying SKILL.md contents or manually maintaining installed versions. Playground's
profile is `rune-playground/docs/agent-skills.md`.

## Official shadcn skill

The official `shadcn` skill is selected in `skills-lock.json` from `shadcn-ui/ui`,
at commit `7c9eaba1c0a6404c990c144a654792e3313c650d`. It was originally installed
with the Codex skill installer and is now managed as a shared Skills CLI snapshot.
This migration preserves the existing instructions; it is not an upstream upgrade.

Use Skills CLI 1.5.24 or newer for this commit URL: 1.5.21 attempts to clone it as
a branch and fails. The reviewed 1.5.24 installer supports fetching a commit SHA.

```bash
npx skills@1.5.24 add https://github.com/shadcn-ui/ui/tree/7c9eaba1c0a6404c990c144a654792e3313c650d/skills/shadcn --agent codex claude-code --skill shadcn -y
```

Bootstrap exposes the canonical snapshot through `~/.agents/skills/shadcn` for
Codex and `~/.claude/skills/shadcn` for Claude. On machines with an older standalone
`~/.codex/skills/shadcn`, compare every file before moving that copy outside skill
discovery; retain a local backup until the shared links and new-task discovery are
verified. Never replace a divergent local copy automatically.

Prefer this official skill for Playground Base UI composition. Vercel's bundled
shadcn capability remains plugin-managed; its presence does not make it the
preferred route or justify copying it into the standalone inventory. Playground's
exploration/graduation policy overrides blanket appearance rules.
