# Maintenance

`agent-tooling` is the canonical consumer configuration for Patrick's shared instructions, locked skill set
and desired plugin state. Codex is the primary harness; Claude Code support is
optional. Patrick-owned skills are released from `pdugan20/skills`. Default bootstrap and setup checks target Codex; use the explicit Claude commands for its optional harness.
See [setup boundaries](setup.md#current-command-boundary).

## Tasks

- [Shared instructions](#update-shared-instructions) and [Patrick skills](#update-patrick-skills)
- [Upstream skills](#update-upstream-skills) and [freshness checks](#read-only-skill-freshness-and-usage)
- [Repository verification](#verify-repository-changes) and [releases](#release-agent-tooling)
- [Catalog](#maintain-the-catalog) and [machine audits](#audit-a-machine)
- [Codex plugins](#refresh-installed-codex-plugins) and [optional Claude plugins](#refresh-optional-claude-plugins)
- [Retired Superpowers plugin](#remove-the-retired-superpowers-plugin)

## Update shared instructions

1. Edit the canonical file in this repository.
2. Run Markdown and repository policy checks; include configuration tests when changing setup contracts.
3. Regenerate the catalog when skill metadata or plugin state changes.
4. Commit and push this repository.
5. On another machine, pull, run `npm run bootstrap`, and start a new Codex task; use `npm run bootstrap:claude` for Claude.

## Update Patrick skills

1. Edit and validate the canonical skill in `pdugan20/skills`.
2. Release a new semantic version there.
3. Install that exact tag here with Skills CLI. The current consumer retains Codex and Claude compatibility links.
4. Review `.agents/skills/`, `.claude/skills/`, and `skills-lock.json`.
5. Regenerate the catalog, run `npm run bootstrap`, and start new Codex tasks. Run `npm run bootstrap:claude` when updating Claude links.

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

`npm run verify` recomputes each snapshot's hash the way Skills CLI does and compares it with `computedHash` in
`skills-lock.json`, so an edit to a snapshot that did not come from a Skills CLI install fails CI. Skills CLI hashes
the upstream source before installing it, so a few locked hashes cannot be recomputed from the installed copy: upstream
files the installer leaves out, such as `metadata.json`, and links it turns into real files. Those skills are listed in
`config/skill-snapshot-hashes.json` with the lock hash, the installed tree hash, and the reason. The check fails when
an exception goes stale, so after updating one of those skills, compare the new install with upstream at its ref
(`npm run skills:check`) and then update or remove its entry. `node scripts/check_skill_snapshots.mjs --print` prints
the installed tree hashes.

Skill updates remain deliberately reviewed. Use the existing CLI install and update path, inspect instruction
changes, and preserve provenance. No scheduled skill-update or auto-merge workflow is configured here.

On 2026-11-25, SwiftUI Pro was updated to the exact upstream commit
`f2920b63995263f57b3e198674e89a602efba6d2` using Skills CLI 1.7.4:

```bash
npx skills@1.7.4 add https://github.com/twostraws/swiftui-agent-skill/tree/f2920b63995263f57b3e198674e89a602efba6d2/swiftui-pro --agent codex claude-code --skill swiftui-pro -y
```

The entrypoint still declares 2.0.0. Upstream moved its Claude plugin manifest to the repository root and removed
the nested compatibility copy, so the snapshot holds one `SKILL.md` and one reference tree of twelve documents.
Bootstrap no longer disables a duplicate, the lock hash recomputes from the installed files, and repository policy
fails when any locked snapshot contains a nested skill. The update also corrects three examples: a named closure
parameter in the binding setter, `try` on the throwing `Date` parser, and selection order in the reorder helper.
The upstream MIT copyright and license notice is retained in [licenses/swiftui-pro.txt](licenses/swiftui-pro.txt),
outside the hash-tracked skill snapshot because upstream keeps its `LICENSE` at the repository root.

During review, preserve its existing-target and toolchain checks, bounded feature/fix scope, and binding-setter
behavior caveats. Deep performance restructuring requires a requested deep review or an established performance
problem. Source and packaging verification does not establish iOS or device runtime behavior.

Before this update the snapshot carried a nested copy, and Claude listed both `swiftui-pro` and
`swiftui-pro:swiftui-pro` because the directory contained `.claude-plugin/plugin.json`. Measured on 2026-09-17 from
the `skills` list in a headless `stream-json` init event:

- `skillOverrides` with the key `swiftui-pro:swiftui-pro` changes nothing.
- `skillOverrides` with the key `swiftui-pro` hides the top-level copy and keeps the nested one.
- `enabledPlugins` with `swiftui-pro@skills-dir` set to `false` hides both copies.

The same package shape can affect `swift-testing-pro` in repositories that lock it. Leave such a duplicate in place
and do not edit the snapshot to remove it.

On 2026-11-25, Stageshow was updated to the exact upstream commit
`299140fafd08df55a9c234e610c3f64af3f45531`, release 1.1.1, using Skills CLI 1.7.4:

```bash
npx skills@1.7.4 add https://github.com/benjitaylor/skills/tree/299140fafd08df55a9c234e610c3f64af3f45531/stageshow --agent codex claude-code --skill stageshow -y
```

Releases 1.1.0 and 1.1.1 add the `Button`, `Card`, `Divider` and `Draft` kit parts with their specimens, tell
agents to restyle a kit part before hand-building a lookalike, tighten the filming checks, and fix a playground
layout shake.

Repository policy requires that commit, so moving to a newer upstream revision is a reviewed change to
`STAGESHOW_REF` and the lock together. The skill is MIT licensed, but its bundled app icons and brand marks keep
their own terms, listed in its `NOTICE.md` and `kit/brands/SOURCES.md`. Keep the snapshot unmodified.
Stageshow's workflow installs packages and films output beside its examples; the shared agreement directs agents
to do that work in the target project instead, because the installed folder links back to this checkout.

## Verify repository changes

Install the [verification prerequisites](setup.md#develop-this-repository), then run:

```bash
npm run verify
```

This is the exact `ci` status check used by GitHub Actions. It validates the canonical files and repository policy
without inspecting authenticated runtime state. Continue to use `npm run setup:check` separately after applying the
setup on a real machine.

ClaudeLint remains in the repository gate for Claude configuration files. It does not validate skill snapshots:
`claudelint validate-skills` ignores `--path`, and `.claudelintignore` excludes the snapshot directories, so the former
`validate-skills --path .agents/skills` step checked nothing. Patrick-owned skills are validated in Skills before release,
and the snapshot hash check confirms every locked snapshot is unmodified. Do not reformat or patch upstream snapshots
locally. Repository policy separately checks lock provenance, compatibility links, and desired plugin
state.

### Secret scanning

GitHub secret scanning and repository push protection are enabled. Gitleaks remains an independent defense-in-depth
check at three points:

- staged changes in the local pre-commit hook;
- full Git history in the local pre-push hook;
- full Git history in required GitHub Actions `ci` and release verification.

Install both local hooks with `pre-commit install --hook-type pre-commit --hook-type pre-push`. CI checkouts must retain `fetch-depth: 0`; repository policy validation guards that invariant.

## Release agent tooling

GitHub releases describe the complete repository setup and use ordinary SemVer tags. `package.json` is the
repository version source.

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

The script upgrades only marketplaces named by the selected CLI plugin manifest, re-adds each selected plugin, and
reapplies Codex configuration fixes. It honors `CODEX_HOME` and preserves unselected plugins and marketplaces. Re-adding an installed plugin refreshes its recorded version without an uninstall. Start a fresh chat to
check the result. This command does not update the Codex application or guarantee an account-managed plugin refresh.

Setup installation preserves existing plugins and caches, including retired IDs. It only adds selected plugins that
are missing. `npm run setup:check` checks the selected enabled set and fails while a Superpowers plugin is
still enabled; that installation remains intact for explicit removal. Claude configuration also stops
when its settings explicitly enable official Superpowers; it preserves the settings file instead of disabling that plugin. Legacy cleanup is a separate decision.
Account-managed plugins listed in
`config/codex-managed-plugins.txt` must be checked in the Codex Plugins tab because the CLI does not authoritatively
report that separate layer.

The scripts use `codex plugin marketplace upgrade <name>` and `codex plugin add`. Check the installed CLI help before
changing those primitives. Inspect CLI and desktop versions separately; they can use different binaries.

Patrick's Mintlify skills are installed from the same tagged `pdugan20/skills`
release as the design and delivery skills. The separate `mintlify-docs` plugin is
retired; setup and refresh preserve an existing installation until its owner approves retirement. Mintlify's official
plugin remains installed for current product mechanics.

## Refresh optional Claude plugins

Refresh Claude Code plugins when maintaining its native harness:

```bash
npm run plugins:refresh:claude
```

Underneath, this runs `claude plugin marketplace update <name>` and `claude plugin update` for the entries in
`config/claude-plugins.txt`. Restart Claude afterward. Selecting a Claude model in Codex does not require this step.

`npm run setup:check:claude` requires the selected plugins and no enabled Superpowers plugin. Setup preserves
undeclared user plugins and their enablement; refresh does too. Marketplace updates are limited to selected names.
The retained `scripts/reconcile_claude_plugins.py` helper can report undeclared IDs from supplied JSON, but setup and
refresh do not use that report to disable or remove anything. Review ownership separately before retirement.

Capabilities needed by only one repository belong with that repository instead of this global manifest. For
example, `rss-feed-generator` pins Railway's canonical `use-railway` Agent Skill once under `.agents/skills` and
links it into Claude. This gives both agents the same project-scoped source without installing either runtime's
Railway plugin globally.

The `.agents/skills/` snapshots and `.claude/skills/` compatibility links give
both runtimes the same Patrick-owned skill contents without a second plugin
installation.

## Remove the retired Superpowers plugin

This setup selected a configured fork of [`obra/superpowers`](https://github.com/obra/superpowers) until 2026-11-25.
Its strict workflows were already explicit-only here, and the verification rules it still
supplied now live in `global/AGENTS.md`. Setup never uninstalls plugins, so remove it once on each machine that had it:

```bash
codex plugin remove superpowers@superpowers-configured
codex plugin marketplace remove superpowers-configured
claude plugin uninstall superpowers@superpowers-configured
claude plugin marketplace remove superpowers-configured
```

Run the Claude commands only where Claude Code had the plugin. `npm run bootstrap:claude` removes the fork's
`enabledPlugins` entry from Claude settings, and the setup checks fail while any Superpowers plugin is still enabled.

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
copying SKILL.md contents or manually maintaining installed versions.

## Official shadcn skill

The official `shadcn` skill is selected in `skills-lock.json` from `shadcn-ui/ui`,
at commit `4233ed1caded8c38f4bc14b14afe1f93ebcaf966`. It was originally installed
with the Codex skill installer, moved to a shared Skills CLI snapshot at
`7c9eaba1c0a6404c990c144a654792e3313c650d`, and updated on 2026-11-25. The update adds
the DESIGN.md design-system workflow with its showcase assets and coverage script, and
`Trace` guidance for assistant activity in chat interfaces.

Use Skills CLI 1.5.24 or newer for this commit URL: 1.5.21 attempts to clone it as
a branch and fails. The update used 1.7.4.

```bash
npx skills@1.7.4 add https://github.com/shadcn-ui/ui/tree/4233ed1caded8c38f4bc14b14afe1f93ebcaf966/skills/shadcn --agent codex claude-code --skill shadcn -y
```

Default bootstrap exposes the canonical snapshot through `~/.agents/skills/shadcn` for
Codex; `bootstrap:claude` adds `shadcn` to the active Claude profile. On machines with an older standalone
`~/.codex/skills/shadcn`, compare every file before moving that copy outside skill
discovery; retain a local backup until the shared links and new-task discovery are
verified. Never replace a divergent local copy automatically.

Prefer this official skill for Playground Base UI composition. Vercel's bundled
shadcn capability remains plugin-managed; its presence does not make it the
preferred route or justify copying it into the standalone inventory. Playground's
exploration/graduation policy overrides blanket appearance rules.

## Audit a machine

Use this checklist when reconciling the portable setup with a working machine.
The [ownership guide](capability-ownership.md) distinguishes source decisions, product scope, and private bindings. Keep the report private and dated;
record source, resolved path, version or hash, owner, and evidence of effective availability separately.

1. Identify the shell CLI, desktop runtime, active configuration directories, and any provider or proxy layer.
   Read the shared agreement's private-note routing before account or proxy diagnosis.
2. Inventory instruction and configuration layers, including overrides, project trust, local hooks, execution rules,
   and notification handlers. Record what installs each customization.
3. Inspect user `.agents/skills`, legacy `.codex/skills`, optional Claude skills, and plugin-bundled skills.
   Classify links to this repo, links to other checkouts, standalone copies, runtime bundles, and broken links.
   A global Skills CLI lock is a separate provenance record from this repo's `skills-lock.json`.
4. Compare selected plugin manifests with CLI-visible installations and the desktop account or workspace view.
   Inspect project-local enablement separately. Cached packages do not prove active installation.
5. Compare the standalone MCP manifest with local and plugin-provided server metadata. Record ownership and
   authentication status without printing credentials, environment values, or raw configurations.
6. Inventory project instruction, skill, hook, and config surfaces within an explicitly bounded repository set.
   Include other clients only where they add relevant local or organization-managed tooling.
7. Report duplicate names, divergent contents, unknown provenance, broken links, and coverage limits. Recommend
   ownership or retirement decisions before any deletion, relinking, installation, or runtime change.

`npm run catalog:snapshot` is useful evidence, but it checks selected skills rather than discovering arbitrary
standalone copies. Its project scan reads immediate child primary repositories and skips linked worktrees.
The current catalog also infers invocation labels from metadata; use [runtime-specific controls](skill-invocation.md)
and the active chat to verify them.

A machine inventory is not a behavioral or security audit of every skill and tool. Avoid reading credential stores,
conversation history, or raw service logs for an ownership inventory. Preserve local work and approval boundaries
when deciding what to adopt, keep private, or retire.
