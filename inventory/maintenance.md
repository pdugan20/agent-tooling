# Agent tooling maintenance

`agent-tooling` is the single canonical source for Patrick's shared instructions, personal skills, desired plugin
state, and configured Superpowers baseline. Claude and Codex consume the same personal skill files through
runtime-specific symlinks; do not maintain separate copies.

## Update personal instructions and skills

1. Edit the canonical file in this repository.
2. Validate affected skills with `quick_validate.py` and run the repository's configuration tests.
3. Regenerate the catalog when skill metadata or plugin state changes.
4. Commit and push this repository.
5. On another machine, pull, run `./scripts/bootstrap.sh`, and start a new Claude or Codex task.

After changing a personal skill, rerun `./scripts/bootstrap.sh` and start new tasks. The symlinks update immediately,
but active tasks retain the skill inventory loaded when they started.

## Verify repository changes

Install the repository development dependencies once as documented in `README.md`, then run:

```bash
npm run verify
```

This is the exact `ci` status check used by GitHub Actions. It validates the canonical files and repository policy without inspecting authenticated runtime state. Continue to use `./scripts/verify-setup.sh` separately after applying the setup on a real machine.

ClaudeLint is intentionally strict. Fix new warnings rather than adding broad suppressions. The one file-scoped
override handles Swift closure syntax such as `$0`, which ClaudeLint otherwise mistakes for a skill argument.
`scripts/validate_repository.py` separately validates the configured Superpowers baseline and desired plugin state.

### Secret-scanning fallback

GitHub-native secret scanning and push protection are unavailable for this user-owned private repository under the current account model. GitHub documents private-repository Secret Protection as an organization or enterprise product, so enabling it would require a separate ownership, plan, and billing decision.

The repository instead fails closed through Gitleaks at three points:

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
4. Create and push an annotated repository tag from that merge commit:

   ```bash
   git tag -a v0.3.0 -m "v0.3.0"
   git push origin v0.3.0
   ```

5. Confirm the release workflow created a GitHub Release titled `v0.3.0` with the matching curated changelog notes.
6. On each machine, pull and rerun the relevant bootstrap or refresh commands from the release's upgrade notes.

The release workflow rejects malformed tags, tags that differ from the root package version, and versions without a
changelog section. It publishes release notes only; it does not publish an npm package, update runtime caches, or
install plugins on other machines.

Patrick Delivery's historical `patrick-delivery-v0.2.0` tag remains valid history. Future GitHub releases use the
repository-wide `vMAJOR.MINOR.PATCH` convention.

## Maintain the catalog

The committed `catalog/data.json` file is generated from skill frontmatter, plugin manifests, desired plugin lists,
and `catalog/plugin-metadata.json`. Do not hand-edit it.

```bash
npm run catalog:generate
npm run catalog
```

When a configured third-party plugin changes, update its short descriptive metadata only if the existing description
is no longer accurate. CI runs `npm run catalog:check` and fails when generated data drifts from canonical inputs.

For a private runtime comparison, run `npm run catalog:snapshot`. The resulting
`catalog/runtime-data.local.json` contains only capability identifiers, versions, runtime state, and repository
metadata—not installation paths, credentials, or plugin configuration—and is ignored by Git.

## Refresh installed Codex plugins

Run:

```bash
./scripts/refresh-codex-plugins.sh
```

The script refreshes Git marketplace snapshots, re-adds every configured plugin in place, reapplies the Product Design skill overrides, and reminds you to start a new task. Re-adding an installed plugin refreshes its recorded version without an uninstall. OpenAI-curated and bundled local marketplaces are refreshed by Codex application or CLI updates; the add uses whichever snapshot that installation currently exposes.

The current Codex CLI has no `plugin update` command. Its relevant refresh primitives are `codex plugin marketplace upgrade` and `codex plugin add`.

Refresh the desired Claude plugin set with:

```bash
./scripts/refresh-claude-plugins.sh
```

Underneath, this runs `claude plugin marketplace update` and `claude plugin update` for the entries in `config/claude-plugins.txt`. Claude requires a restart after a plugin update.

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
6. Run `./scripts/refresh-codex-plugins.sh` and `./scripts/refresh-claude-plugins.sh`, restart both products, and run
   `./scripts/verify-setup.sh`.
7. Start new tasks and smoke-test one automatic workflow (for example debugging) plus negative prompts for TDD,
   brainstorming, worktrees, and the browser option picker.

The current baseline is upstream `6.2.0` at commit
`3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`; the configured fork version is `6.2.0-config.1`.

## Product Design policy

Patrick's default visual ideation surface is runnable code in the real project, browser, or relevant simulator. Generated-image ideation is opt-in.

`scripts/configure-codex.py` disables Product Design's `index` router and `ideate` skill when their installed cache paths are present. It intentionally leaves audit, URL-to-code, image-to-code from an existing reference, design QA, research, user context, and sharing available. Because plugin cache paths include versions, rerun `./scripts/bootstrap.sh` after a Codex or Product Design update, then start a new task.
