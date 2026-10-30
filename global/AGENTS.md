# Personal Codex Working Agreement

Apply this guidance across repositories unless a nearer `AGENTS.md` overrides it.

This file is published in a public repository. Keep employer, client, and
teammate names, ticket identifiers, and private notes out of it; put
organization rules in that organization's repositories and personal notes in
`~/.codex/local/`, which no repository tracks.

## Discover existing homes before adding new components

Before proposing or implementing a new tool, integration, automation, service,
shared component, or repository, check beyond the current checkout. Read the
applicable project guidance, search existing implementations, and refresh the
current organization's accessible repository inventory. Inspect likely
repositories' READMEs and relevant code before choosing where the work belongs.
An empty code-search result does not establish that no suitable repository exists.

Read `~/.codex/local/project-discovery.md` when present for verified starting
points. These notes are a cache, not an exhaustive or authoritative inventory;
discover new repositories and verify relevant entries against current sources.
Record useful findings privately with source links and a checked date. Keep
organization-specific names and routing out of this public working agreement.

Before implementation, briefly report the candidates inspected and why to reuse,
extend, or create. State any access or coverage gap instead of claiming absence.
Keep discovery proportional: routine changes in an established component do not
need an organization-wide search. This check does not require a new skill,
formal plan, worktree, or permission request, and grants no new access or
publication authority.

## Personal branch names

For branches created for Patrick, use the personal policy in
`~/.codex/local/branch-naming/policy.json`. It replaces the app's `codex/`
default: choose the work type, include an existing issue ID when available,
and use a concise lowercase hyphenated description. Ticketless exploration
is allowed. Read the policy before creating or renaming a branch and use a
literal name in a direct Git command or a structured branch-creation tool.
Do not hide branch creation inside scripts, Git aliases, or interactive stdin.
Checking out and continuing existing branches is allowed. Preserve published
branches with open PRs until they finish; do not rename someone else's branches.
This is Patrick's personal preference, not shared repository policy. A matching
personal PreToolUse hook validates supported branch-creation and rename calls.

## Chat titles

Name every new chat or session with a short lowercase slug of one to three
hyphenated words: the project or surface first, then the task when it adds
meaning. Examples: `sony-tv-polish`, `listening-page-polish`, `inflight-eval`,
`opencodex-setup`, `calendar-setup`. Avoid sentences, title case, articles,
dates, ticket noise, and prefixes such as `codex/`. In the Codex app, set the
title with `set_thread_title` once the task is clear in the first turn, and
retitle only when the task changes substantially. In other runtimes, use the
equivalent rename command when one is available. Keep a title Patrick set
himself unless he asks for a new one.

## Choose the lightest useful mode

### Local preview controls

- Always include the current local-network (LAN) URL when sharing a local development preview, with the port and relevant route. Do not provide only localhost. Detect the active LAN IP each time and verify the preview responds through it; do not reuse a stale address.
- Keep TanStack Query Devtools and its floating launcher disabled in Patrick's local previews across sessions. For projects using Vite, preserve `VITE_SHOW_IN_APP_QUERY_DEV_TOOLS=false` when starting or restarting Vite, including in new worktrees, detached sessions, and sanitized environments. Do not enable it unless Patrick explicitly asks.

### Temporary checkout lifecycle

- Keep permanent repositories in `Documents/Github`. Do not create sibling task-specific clones or worktrees there; reuse the current checkout for ordinary exploration.
- When an isolated checkout is justified and allowed, prefer an existing suitable checkout or an app-managed worktree outside `Github`. This does not make worktrees or strict workflows mandatory. Record its purpose, owner chat, branch, shared-object dependencies, and retirement condition.
- At batch closeout, report which temporary checkouts are still needed and which can be archived or removed. Preserve unfinished work, recoverable Git history, needed ignored configuration, and useful evidence before cleanup; check running processes and dependent checkouts first.
- Use the app's archive action for app-managed worktrees and Git worktree removal for manually managed worktrees. Preserve needed ignored files separately. Local deletion, branch deletion, pushes, and PR changes retain their existing authorization boundaries; do not treat a closed PR or archived chat as permission to discard local work.

### Exploration (default)

Use for visual design, UI variants, motion tuning, prototypes, copy changes, and quick experiments.

- Iterate directly in code or the browser.
- Do not require a formal spec, implementation plan, worktree, test-first cycle, or commit.
- Keep changes easy to inspect and undo.
- Verify the changed surface proportionally: render it, exercise the interaction, take a screenshot when useful, and run a focused compile or check when practical.
- Ask before expanding a small design iteration into architecture or production hardening work.

## Code-native visual ideation

- Never invoke `product-design:index`, `product-design:ideate`, or use ImageGen unless Patrick explicitly requests image generation or image mockups.
- When Patrick asks to brainstorm, explore, revise, or compare UI directions, use the `code-native-ui-ideation` skill and ideate directly in working code.
- Build runnable variants in the existing project or a lightweight project-native workbench so they can be compared in the browser or relevant simulator.
- Present UI variants through an in-place toggle or keyboard shortcut on the same preview surface; do not send separate demo URLs for each option.
- Do not replace live code variants with generated images, static mockups, or a separate browser-based option picker.
- Treat image generation as opt-in, never inferred from phrases such as “visual revs,” “standalone versions,” “brainstorm,” or “compare directions.”

### Production

Use when Patrick says `ship`, `merge`, `release`, `PR`, `production`, or `harden`, or clearly asks for production-ready implementation.

- Preserve the chosen design and remove experiment-only paths.
- Add tests according to regression risk; test-first development is optional unless explicitly requested.
- Check relevant accessibility, failure states, loading states, and platform behavior.
- Run focused verification first, then the appropriate broader checks before claiming readiness.
- Do not deploy, mutate production data, push, or open a PR without explicit authorization.
- Repositories may create PR previews automatically, including for drafts. That CI
  behavior alone grants no authority for additional deployment, configuration, or data
  writes. When Patrick explicitly requests preview verification, the request covers the
  necessary non-secret preview values on a documented companion branch named after the
  PR branch, including its push and preview redeploy. An explicitly requested preview
  label can express that intent, but label presence is not required. Preserve earlier
  authorization and honor narrower limits such as read-only or no-push instructions.
  Shared base values, default branches, secrets, data resets, and anything that reaches
  a real environment still require explicit approval. Verify the final deployed revision
  and applied values before accepting preview evidence; a warm URL or values push alone
  is insufficient.
- For a substantial production feature spanning meaningful behavior or multiple subsystems, allow the personal `feature-delivery` skill to apply automatically.

### Hardening

Use only when explicitly requested. Audit edge cases, accessibility, performance, security, observability, test coverage, and release readiness in proportion to the feature's risk.

## Strict workflows are opt-in

The configured Superpowers fork enforces explicit-only invocation for brainstorming, strict TDD, implementation planning and execution, worktrees, parallel-agent orchestration, the full Superpowers router, and branch finishing. Use those workflows only when Patrick names the skill or explicitly requests that workflow.

In Codex, invoke strict workflows with `$superpowers:<skill-name>`. In Claude, use `/superpowers:<skill-name>`. Common examples are `brainstorming`, `test-driven-development`, `writing-plans`, `executing-plans`, `using-git-worktrees`, and `finishing-a-development-branch`.

The personal `feature-delivery` skill is the exception: it may trigger automatically for substantial production feature implementation. It uses proportional planning, risk-based testing, implementation checkpoints, and production verification without implicitly invoking strict TDD, mandatory brainstorming, worktrees, or branch-finishing workflows. When a selected implementation needs a dedicated release-readiness audit, ask for hardening explicitly and follow the repository's production instructions or a separately requested release-readiness capability.

The configured Superpowers plugin is maintained as a thin fork of `obra/superpowers`. It disables the always-on session bootstrap and removes the brainstorming Visual Companion/browser option-picker. Do not restore either behavior through repository-level instructions.

When a repository installs the `mattpocock/skills` planning set, the split is: Superpowers keeps the plan document and its execution (`writing-plans`, `executing-plans`, `subagent-driven-development`); `grill-with-docs` owns decisions recorded as ADRs and glossary terms; `to-tickets` and `wayfinder` own the issue-tracker layer (tracer-bullet tickets with blocking edges, multi-session decision maps). Do not add a skill that duplicates either side, and do not fan out for planning.

## Bounded batch authorization

- When Patrick approves a named, finite batch (for example, "continue through the rest of Batch 1" or "do all recommended items in this batch"), treat that as authorization to complete the identified items without stopping for routine confirmations between them.
- State the batch boundary before execution, keep progress updates informational, and report once the batch reaches a clear verification or decision boundary. A progress update is not a request for Patrick to re-authorize the next item.
- Explicit-only planning and tracker skills remain explicit-only. Use them to create or resolve the map, decision, or ticket artifact they own. Once the artifact contains a decided implementation batch, execute that batch through the repository's ordinary delivery cycle; do not repeatedly invoke the planning skill, and do not claim it ran during ordinary implementation.
- Repeated skill invocation is required only when the next item genuinely needs the skill to perform a new gated action, such as changing the map, publishing tickets, or conducting another owner-approved analysis pass. A historical skill mention or an already-decided ticket does not require another invocation.
- Batch authorization never expands scope to a new product decision, dependency, destructive action, live-data mutation, deployment, push, pull request, or merge unless the applicable repository rules and Patrick's authorization already allow it. Pause when evidence contradicts the agreed direction or when one of those real boundaries is reached.

## Agent cost discipline

- Multi-agent review and research are fine; run the workers (finders, verifiers, research sweeps) on the cheapest model that can do the job and reserve the expensive tier for orchestration and judgment. Never fan out on the expensive tier without first stating the model, the agent count, and the expected cost.
- Pick review depth by change class: docs, config, and skill snapshots get no agent review (lint and contract tests are the review); tooling and CI changes get one reviewer subagent at medium effort on a cheap model; product code that touches data, auth, privacy, or sync gets a multi-agent review with cheap workers and one expensive judge, or the runtime's equivalent independent deep review (`/code-review ultra` in Claude is cloud-hosted, separately billed, and user-triggered).
- Prefer fresh-context subagents to forks; a fork copies the whole conversation into every worker, so use it only when the conversation itself is the input.
- Work in stated batches (for example "finish these two tickets, then report") and report at the end of each batch with what ran, roughly what it cost, and what is next; do not chain unbounded work.

## Apple build, Simulator, and runtime evidence

- Prefer the pinned XcodeBuildMCP capability for Apple project discovery, builds, tests, launches, semantic Simulator actions, captured runtime logs, and LLDB inspection when its tools are available.
- Keep automated Apple build artifacts bounded. Builds from temporary clones or worktrees must set a stable DerivedData location per canonical project; never allow each worktree path to create a new cache under Xcode's default global DerivedData directory.
- Reuse one DerivedData location for serial automation. For concurrent builds, use a fixed, small pool keyed by worker slot and clean the slot when its task ends; do not create an unbounded cache keyed by task, thread, clone, or worktree ID.
- After `session_show_defaults`, treat a missing or worktree-local `derivedDataPath` as incomplete XcodeBuildMCP context. Set it with `session_set_defaults` to a bounded path under `~/DerivedData/<canonical-project>-slot-<n>` before building or testing; use the serial slot unless the task is explicitly running concurrent Apple builds.
- For repository-supported `xcodebuild` fallbacks, pass the same bounded path with `-derivedDataPath`; do not rely on Xcode's implicit global cache location from a temporary checkout.
- Use computer use for perceptual and visual judgment, Simulator chrome and permissions, coordinate-only or custom-rendered controls, and interactions whose accessibility tree is incomplete. Refresh semantic snapshots after navigation or layout changes; element references are screen-state scoped.
- Use Instruments or `xctrace`, and physical-device or distribution evidence when the performance claim requires them. A successful build, semantic UI snapshot, Simulator stack, or aggregate FPS reading does not establish animation smoothness or device performance.
- For a visual performance problem, use structured automation to reproduce and gather logs, computer use or recordings to judge the visible miss, and Instruments to attribute missed deadlines. Keep the scenario, build, cache, network, and device conditions equivalent across comparisons.
- Fall back to repository-supported `xcodebuild`, `xcrun`, or `simctl` commands when XcodeBuildMCP is unavailable or cannot represent the required surface; do not block ordinary Apple work on the integration.

## Firebase and Firestore safety

- Prefer emulators for development, rules tests, destructive experiments, and bulk operations.
- Before any live Firebase operation, identify the active project and state whether it is development, staging, or production.
- Require explicit approval before deploying or mutating live data, Auth users, rules, indexes, functions, or configuration.
- Treat the Admin SDK as privileged: it bypasses Firestore Security Rules and relies on IAM and application checks.
- Never copy raw production data, credentials, tokens, or personal data into prompts, logs, fixtures, or reports.
- For new Firestore query shapes, assess index requirements before treating the implementation as complete.

## Errors in the area you change

An error in the area you are changing is your bug until shown otherwise; find its cause instead of working around it by bumping versions or retrying.

A pending check is not a pass: report merge and CI results per job with their final state, and say "still running" for anything not finished.

## Code Review Rules

- Flag changes that make strict planning, TDD, worktrees, parallel-agent orchestration,
  image generation, deployment, or live-data mutation implicit rather than opt-in.
- Flag skill or plugin changes that duplicate canonical instructions, break portable
  `SKILL.md` content with runtime-specific metadata, or omit relevant routing and
  adversarial evaluation updates.
- Flag instructions that weaken Firebase, credential, production-data, push, PR, or
  destructive-action approval boundaries.

## Skills you cannot invoke

- In Claude, two independent gates control skill invocation: `skillOverrides`, and the
  skill's own `disable-model-invocation` frontmatter. `skillOverrides` cannot override
  the frontmatter, and `user-invocable-only` makes a skill invisible rather than
  approval-gated.
- In Codex, treat the current session's available-skills catalog as authoritative. If a
  skill appears there and the user names it, follow Codex's trigger rules even when the
  portable `SKILL.md` contains Claude's `disable-model-invocation` field. Do not
  reinterpret that Claude-specific field as a Codex block. See the consuming
  repository's `docs/skill-invocation.md`.
- **If a ticket, plan, or doc requires an action from a skill you cannot invoke: stop and
  ask the owner to run it.** Do not substitute a hand-rolled equivalent, and do not
  quietly proceed without it. A historical mention or already-decided implementation
  ticket does not require another invocation.
- Invisible tooling does not get skipped, it gets silently substituted. An agent that
  cannot see a tool builds its own version and does not mention the swap, so the owner
  believes the named tool ran.

## Project product writing

- Before drafting or editing issue-tracker or knowledge-base content, follow the consuming project's writing instructions and required skills. Keep organization-specific routing in that project.

## Instruction files

Treat `AGENTS.md` as the canonical cross-agent instruction file. A repository may keep `CLAUDE.md` as a compatibility shim or for genuinely Claude-specific guidance. Preserve existing user work and follow the nearest applicable instruction file.

Claude Code 2.1.277 and later reads a repository's `AGENTS.md` natively when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or above it; `~/.claude/CLAUDE.md` does not count. The shared `SessionStart` hook from `agent-tooling` supplies `AGENTS.md` only when that native loading does not apply (older version, or a project Claude file present), so the file is never injected twice. Do not add `CLAUDE.md` or hidden, git-excluded `CLAUDE.local.md` shims to a repository only to load `AGENTS.md`. If a session shows no repository instructions, check the installed version and the hook before adding a file. Neither path loads nested `AGENTS.md` files below the working directory, so read those before editing in their directories.

## Private account and machine notes

Before diagnosing account or connector authentication, model routing, missing or denied local tools, or anything involving the OpenCodex proxy, read `~/.codex/local/account-notes.md` if it exists. It points to the private OpenCodex runbook (`~/.codex/local/opencodex-runbook.md`), which owns proxy setup, routing, the upgrade procedure, and troubleshooting; read the runbook before changing or upgrading the proxy. Keep account/machine-specific troubleshooting in those private local files, not in project documentation or shared trackers. Never store credentials or tokens in notes.

Before sharing a pull request link, read `~/.codex/local/pr-links.md` if it
exists. Before drafting text Patrick will post, or that is posted under his
name, read `~/.codex/local/writing-voice.md` if it exists.

## OpenCodex tool catalogs

Sessions may run through the local OpenCodex proxy. For Claude, prefer an
`anthropic/<model>` row; Codex tools pass through unchanged there. On
`cursor/*` models the listed local tool set changes per request (sometimes
Cursor-native `Shell`/`Read`/`Glob`/`Grep`, sometimes Codex `exec` with nested
`tools.*`) and listed Cursor-native tools may still be denied. This is known
proxy behavior, not a fault in the session. When a top-level local tool is
missing or denied, do not retry it; reach `exec` through the dynamic-tool
namespace (`GetDynamicTools` with pattern `^exec$`, then `CallDynamicTool` in
namespace `opencodex-responses`), which works in every request. Read a deferred
tool's schema before its first call instead of guessing argument names. For
thread coordination, `wait_threads` may fail; poll `read_thread`. Procedure
and history live in `~/.codex/local/opencodex-runbook.md`.
