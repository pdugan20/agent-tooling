# Personal Codex Working Agreement

Apply this guidance across repositories unless a nearer `AGENTS.md` overrides it.

## Choose the lightest useful mode

### Exploration (default)

Use for visual design, UI variants, motion tuning, prototypes, copy changes, and quick experiments.

- Iterate directly in code or the browser.
- Do not require a formal spec, implementation plan, worktree, test-first cycle, or commit.
- Keep changes easy to inspect and undo.
- Verify the changed surface proportionally: render it, exercise the interaction, take a screenshot when useful, and run a focused compile or check when practical.
- Ask before expanding a small design iteration into architecture or production-hardening work.

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
- For a substantial production feature spanning meaningful behavior or multiple subsystems, allow `patrick-delivery:feature-delivery` to apply automatically.

### Hardening

Use only when explicitly requested. Audit edge cases, accessibility, performance, security, observability, test coverage, and release readiness in proportion to the feature's risk.

## Strict workflows are opt-in

Do not invoke Superpowers planning, brainstorming, TDD, worktree, or branch-finishing workflows implicitly. Use them only when Patrick names the specific skill or explicitly asks for that workflow.

Patrick's strict component workflows remain explicit-only. In Codex, invoke `$patrick-delivery:formal-spec`, `$patrick-delivery:strict-tdd`, `$patrick-delivery:write-plan`, `$patrick-delivery:execute-plan`, or `$patrick-delivery:production-hardening`. In Claude, use the direct personal-skill equivalents `/formal-spec`, `/strict-tdd`, `/write-plan`, `/execute-plan`, and `/production-hardening`.

`patrick-delivery:feature-delivery` is the exception: it may trigger automatically for substantial production feature implementation. It uses proportional planning, risk-based testing, implementation checkpoints, and production verification without implicitly invoking strict TDD, mandatory brainstorming, worktrees, or branch-finishing workflows.

## Firebase and Firestore safety

- Prefer emulators for development, rules tests, destructive experiments, and bulk operations.
- Before any live Firebase operation, identify the active project and state whether it is development, staging, or production.
- Require explicit approval before deploying or mutating live data, Auth users, rules, indexes, functions, or configuration.
- Treat the Admin SDK as privileged: it bypasses Firestore Security Rules and relies on IAM and application checks.
- Never copy raw production data, credentials, tokens, or personal data into prompts, logs, fixtures, or reports.
- For new Firestore query shapes, assess index requirements before treating the implementation as complete.

## Instruction files

Treat `AGENTS.md` as the canonical cross-agent instruction file. A repository may keep `CLAUDE.md` as a compatibility shim or for genuinely Claude-specific guidance. Preserve existing user work and follow the nearest applicable instruction file.
