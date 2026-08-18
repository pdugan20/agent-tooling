# Personal Codex Working Agreement

Apply this guidance across repositories unless a nearer `AGENTS.md` overrides it.

## Choose the lightest useful mode

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
- Do not replace live code variants with generated images, static mockups, or a separate browser-based option picker.
- Treat image generation as opt-in, never inferred from phrases such as “visual revs,” “standalone versions,” “brainstorm,” or “compare directions.”

### Production

Use when Patrick says `ship`, `merge`, `release`, `PR`, `production`, or `harden`, or clearly asks for production-ready implementation.

- Preserve the chosen design and remove experiment-only paths.
- Add tests according to regression risk; test-first development is optional unless explicitly requested.
- Check relevant accessibility, failure states, loading states, and platform behavior.
- Run focused verification first, then the appropriate broader checks before claiming readiness.
- Do not deploy, mutate production data, push, or open a PR without explicit authorization.
- For a substantial production feature spanning meaningful behavior or multiple subsystems, allow the personal `feature-delivery` skill to apply automatically.

### Hardening

Use only when explicitly requested. Audit edge cases, accessibility, performance, security, observability, test coverage, and release readiness in proportion to the feature's risk.

## Strict workflows are opt-in

The configured Superpowers fork enforces explicit-only invocation for brainstorming, strict TDD, implementation planning and execution, worktrees, parallel-agent orchestration, the full Superpowers router, and branch finishing. Use those workflows only when Patrick names the skill or explicitly requests that workflow.

In Codex, invoke strict workflows with `$superpowers:<skill-name>`. In Claude, use `/superpowers:<skill-name>`. Common examples are `brainstorming`, `test-driven-development`, `writing-plans`, `executing-plans`, `using-git-worktrees`, and `finishing-a-development-branch`.

The personal `feature-delivery` skill is the exception: it may trigger automatically for substantial production feature implementation. It uses proportional planning, risk-based testing, implementation checkpoints, and production verification without implicitly invoking strict TDD, mandatory brainstorming, worktrees, or branch-finishing workflows. When a selected implementation needs a dedicated release-readiness audit, ask for hardening explicitly and follow the repository's production instructions or a separately requested release-readiness capability.

The configured Superpowers plugin is maintained as a thin fork of `obra/superpowers`. It disables the always-on session bootstrap and removes the brainstorming Visual Companion/browser option-picker. Do not restore either behavior through repository-level instructions.

When a repository installs the `mattpocock/skills` planning set, the split is: Superpowers keeps the plan document and its execution (`writing-plans`, `executing-plans`, `subagent-driven-development`); `grill-with-docs` owns decisions recorded as ADRs and glossary terms; `to-tickets` and `wayfinder` own the issue-tracker layer (tracer-bullet tickets with blocking edges, multi-session decision maps). Do not add a skill that duplicates either side, and do not fan out for planning.

## Agent cost discipline

- Multi-agent review and research are fine; run the workers (finders, verifiers, research sweeps) on the cheapest model that can do the job and reserve the expensive tier for orchestration and judgment. Never fan out on the expensive tier without first stating the model, the agent count, and the expected cost.
- Pick review depth by change class: docs, config, and skill snapshots get no agent review (lint and contract tests are the review); tooling and CI changes get one reviewer subagent at medium effort on a cheap model; product code that touches data, auth, privacy, or sync gets a multi-agent review with cheap workers and one expensive judge, or `/code-review ultra` (cloud, separately billed, user-triggered).
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

## Code Review Rules

- Flag changes that make strict planning, TDD, worktrees, parallel-agent orchestration,
  image generation, deployment, or live-data mutation implicit rather than opt-in.
- Flag skill or plugin changes that duplicate canonical instructions, break portable
  `SKILL.md` content with runtime-specific metadata, or omit relevant routing and
  adversarial evaluation updates.
- Flag instructions that weaken Firebase, credential, production-data, push, PR, or
  destructive-action approval boundaries.

## Skills you cannot invoke

- Two independent gates control skill invocation: Claude `skillOverrides`, and the skill's
  own `disable-model-invocation` frontmatter. `skillOverrides` cannot override the
  frontmatter, and `user-invocable-only` makes a skill invisible rather than
  approval-gated. See the consuming repository's `docs/skill-invocation.md`.
- **If a ticket, plan, or doc names a skill you cannot invoke: stop and ask the owner to
  run it.** Do not substitute a hand-rolled equivalent, and do not quietly proceed
  without it. Say which skill you need and why.
- Invisible tooling does not get skipped, it gets silently substituted. An agent that
  cannot see a tool builds its own version and does not mention the swap, so the owner
  believes the named tool ran.

## Instruction files

Treat `AGENTS.md` as the canonical cross-agent instruction file. A repository may keep `CLAUDE.md` as a compatibility shim or for genuinely Claude-specific guidance. Preserve existing user work and follow the nearest applicable instruction file.
